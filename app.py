import io
import tempfile
import time
import streamlit as st
from PIL import Image

# 1. Import Google GenAI
from google import genai

# 2. Import AWS SDK (boto3)
import boto3

# Cấu hình giao diện trang web
st.set_page_config(page_title="Cloud AI Comparison Demo", layout="centered")
st.title("☁️ Demo So Sánh AI: Google Cloud vs AWS")

# Lấy Secrets
gemini_api_key = st.secrets.get("GEMINI_API_KEY")
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
aws_region = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
s3_bucket_name = st.secrets.get("AWS_S3_BUCKET_NAME") # Dùng cho AWS Transcribe

# Chọn Cloud Provider
cloud_provider = st.sidebar.radio(
    "🌐 Chọn nền tảng Cloud Demo:",
    ["1. Google Cloud (Gemini AI)", "2. Amazon Web Services (AWS Native)"]
)

# Chọn tính năng
option = st.sidebar.selectbox(
    "🎯 Chọn loại dữ liệu xử lý:",
    ["Phân Tích Hình Ảnh", "Bóc Băng Âm Thanh / Video"]
)

st.sidebar.divider()
st.sidebar.info("💡 **Gợi ý báo cáo:**\n- **Gemini AI:** Phân tích ngữ cảnh, giải thích sâu, tự nhiên.\n- **AWS Native:** Trích xuất Metadata, nhãn vật thể (JSON) nhanh và tối ưu chi phí.")

# =========================================================
# NỀN TẢNG 1: GOOGLE CLOUD (GEMINI AI)
# =========================================================
if cloud_provider == "1. Google Cloud (Gemini AI)":
    st.subheader("🟢 Google Cloud Platform - Gemini 3.6 Flash")
    
    if option == "Phân Tích Hình Ảnh":
        uploaded_file = st.file_uploader("Tải lên ảnh (JPG, PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Ảnh đầu vào", use_container_width=True)
            
            if st.button("🚀 Phân tích với Gemini AI"):
                try:
                    with st.spinner("Gemini đang quan sát và suy luận..."):
                        client = genai.Client(api_key=gemini_api_key.strip())
                        prompt = "Hãy phân tích chi tiết bức ảnh này: loại ảnh, các đối tượng, văn bản (nếu có) và ý nghĩa tổng quan."
                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[image, prompt]
                        )
                        st.success("Hoàn tất!")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    elif option == "Bóc Băng Âm Thanh / Video":
        uploaded_file = st.file_uploader("Tải lên Audio/Video", type=["mp3", "wav", "mp4", "m4a"])
        if uploaded_file:
            ext = uploaded_file.name.split(".")[-1].lower()
            if st.button("🚀 Bóc băng toàn bộ với Gemini AI"):
                try:
                    with st.spinner("Gemini đang xử lý dữ liệu âm thanh..."):
                        client = genai.Client(api_key=gemini_api_key.strip())
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name
                        
                        audio_file = client.files.upload(file=tmp_path)
                        prompt = "Bóc băng toàn bộ nội dung lời nói trong file âm thanh này và tóm tắt 3 ý chính."
                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[audio_file, prompt]
                        )
                        st.success("Hoàn tất!")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# =========================================================
# NỀN TẢNG 2: AMAZON WEB SERVICES (AWS NATIVE)
# =========================================================
else:
    st.subheader("🟠 Amazon Web Services (AWS Rekognition & Transcribe)")

    if option == "Phân Tích Hình Ảnh":
        uploaded_file = st.file_uploader("Tải lên ảnh (JPG, PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image_bytes = uploaded_file.read()
            st.image(image_bytes, caption="Ảnh đầu vào", use_container_width=True)
            
            if st.button("🚀 Phân tích với AWS Rekognition"):
                try:
                    with st.spinner("AWS Rekognition đang trích xuất nhãn (Labels)..."):
                        rekognition = boto3.client(
                            'rekognition',
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key,
                            region_name=aws_region
                        )
                        
                        response = rekognition.detect_labels(
                            Image={'Bytes': image_bytes},
                            MaxLabels=10,
                            MinConfidence=70
                        )
                        
                        st.success("AWS Rekognition trích xuất thành công!")
                        st.markdown("### 🏷️ Danh sách nhãn vật thể phát hiện được (Labels):")
                        
                        labels_data = []
                        for label in response['Labels']:
                            labels_data.append({
                                "Nhãn (Label)": label['Name'],
                                "Độ tin cậy (Confidence)": f"{label['Confidence']:.2f}%"
                            })
                        st.table(labels_data)

                except Exception as e:
                    st.error(f"Lỗi kết nối AWS Rekognition: {e}")

    elif option == "Bóc Băng Âm Thanh / Video":
        st.info("📌 AWS Transcribe cần lưu file vào AWS S3 Bucket trước khi tiến hành chuyển đổi lời nói thành văn bản.")
        uploaded_file = st.file_uploader("Tải lên Audio (MP3, WAV)", type=["mp3", "wav"])
        
        if uploaded_file:
            if st.button("🚀 Bóc băng với AWS Transcribe"):
                try:
                    with st.spinner("1/3: Đang tải file lên AWS S3 Bucket..."):
                        s3 = boto3.client(
                            's3',
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key,
                            region_name=aws_region
                        )
                        file_name = f"demo_audio_{int(time.time())}.{uploaded_file.name.split('.')[-1]}"
                        s3.upload_fileobj(uploaded_file, s3_bucket_name, file_name)
                        file_uri = f"s3://{s3_bucket_name}/{file_name}"

                    with st.spinner("2/3: AWS Transcribe đang tiến hành bóc băng..."):
                        transcribe = boto3.client(
                            'transcribe',
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key,
                            region_name=aws_region
                        )
                        job_name = f"Transcribe_Job_{int(time.time())}"
                        transcribe.start_transcription_job(
                            TranscriptionJobName=job_name,
                            Media={'MediaFileUri': file_uri},
                            MediaFormat=uploaded_file.name.split('.')[-1],
                            LanguageCode='en-US' # Hoặc 'vi-VN' tùy file gốc
                        )

                        while True:
                            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                            if job_status in ['COMPLETED', 'FAILED']:
                                break
                            time.sleep(3)

                    if job_status == 'COMPLETED':
                        import requests
                        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                        transcript_data = requests.get(transcript_uri).json()
                        text = transcript_data['results']['transcripts'][0]['transcript']
                        
                        st.success("3/3: Bóc băng AWS hoàn tất!")
                        st.markdown("### 📝 Kết quả từ AWS Transcribe:")
                        st.write(text)
                    else:
                        st.error("Quá trình bóc băng trên AWS thất bại.")

                except Exception as e:
                    st.error(f"Lỗi AWS Transcribe/S3: {e}")
