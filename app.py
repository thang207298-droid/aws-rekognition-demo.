import streamlit as st
import boto3
import time
import requests

# ==========================================
# 1. CẤU HÌNH & KHỞI TẠO AWS CLIENTS TỪ SECRETS
# ==========================================
try:
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
    AWS_DEFAULT_REGION = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
    AWS_S3_BUCKET_NAME = st.secrets["AWS_S3_BUCKET_NAME"]
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception as e:
    st.error(f"Lỗi cấu hình Secrets: {e}. Vui lòng kiểm tra lại thiết lập Secrets trên Streamlit Community Cloud.")
    st.stop()

# Khởi tạo S3 Client với Region được lấy động từ Secrets
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

# Khởi tạo Transcribe Client với Region lấy động từ Secrets (Tránh lỗi SubscriptionRequiredException)
transcribe_client = boto3.client(
    'transcribe',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


# ==========================================
# 2. CÁC HÀM XỬ LÝ S3 & AWS TRANSCRIBE
# ==========================================
def upload_file_to_s3(file_bytes, file_name):
    """Tải file âm thanh/video lên S3 Bucket"""
    s3_key = f"transcribe-uploads/{int(time.time())}_{file_name}"
    s3_client.put_object(
        Bucket=AWS_S3_BUCKET_NAME,
        Key=s3_key,
        Body=file_bytes
    )
    s3_uri = f"s3://{AWS_S3_BUCKET_NAME}/{s3_key}"
    return s3_uri

def run_transcribe_job(s3_uri, media_format='mp3'):
    """Tạo và theo dõi Transcribe Job"""
    job_name = f"TranscribeJob_{int(time.time())}"
    
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat=media_format,
        LanguageCode='vi-VN'  # Mặc định tiếng Việt (đổi thành 'en-US' nếu là tiếng Anh)
    )
    
    # Chờ Transcribe hoàn thành
    with st.spinner("Đang xử lý bóc băng âm thanh qua AWS Transcribe..."):
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(3)
            
    if job_status == 'COMPLETED':
        transcript_file_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        response = requests.get(transcript_file_uri)
        result_json = response.json()
        transcript_text = result_json['results']['transcripts'][0]['transcript']
        return transcript_text
    else:
        failure_reason = status['TranscriptionJob'].get('FailureReason', 'Không rõ nguyên nhân')
        raise Exception(f"Transcribe Job thất bại: {failure_reason}")


# ==========================================
# 3. GIAO DIỆN STREAMLIT
# ==========================================
st.set_page_config(page_title="AI Nhận Diện Hình Ảnh Và Âm Thanh", layout="wide")

st.title("☁️ AI Nhận Diện Hình Ảnh Và Âm Thanh")

# Sidebar
with st.sidebar:
    st.header("Chọn nền tảng Cloud Demo:")
    platform = st.radio("", ["1. Google Cloud (Gemini AI)", "2. Amazon Web Services (AWS Native)"], index=1)
    
    st.header("Chọn loại dữ liệu xử lý:")
    data_type = st.selectbox("", ["Bóc Bằng Âm Thanh / Video", "Nhận diện Hình ảnh"])

if platform == "2. Amazon Web Services (AWS Native)":
    st.header("🟠 Amazon Web Services (AWS Rekognition & Transcribe)")
    
    st.info("📌 AWS Transcribe lưu trữ file vào S3 Bucket trước khi trích xuất lời nói.")
    
    uploaded_file = st.file_uploader("Tải lên Audio (MP3, WAV)", type=["mp3", "wav", "m4a"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file)
        
        if st.button("🚀 Bóc băng với AWS Transcribe"):
            try:
                # 1. Tải file lên S3
                with st.spinner("Đang tải file lên S3 Bucket..."):
                    file_bytes = uploaded_file.read()
                    s3_uri = upload_file_to_s3(file_bytes, uploaded_file.name)
                
                # 2. Xác định định dạng file
                ext = uploaded_file.name.split(".")[-1].lower()
                media_format = ext if ext in ["mp3", "wav", "m4a"] else "mp3"
                
                # 3. Gọi AWS Transcribe
                transcript = run_transcribe_job(s3_uri, media_format=media_format)
                
                # 4. Hiển thị kết quả
                st.success("✅ Bóc băng thành công!")
                st.subheader("Trích xuất văn bản:")
                st.write(transcript)
                
            except Exception as e:
                st.error(f"Lỗi AWS Transcribe: {e}")
