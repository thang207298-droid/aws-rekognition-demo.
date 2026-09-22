import io
import tempfile
import time
import streamlit as st
from PIL import Image

# Import Google GenAI SDK
from google import genai

# Import AWS SDK (boto3)
import boto3

# Cấu hình trang Streamlit
st.set_page_config(page_title="Cloud AI Comparison Demo", layout="centered")
st.title("☁️ Demo So Sánh AI: Google Cloud vs AWS")

# Lấy cấu hình từ Streamlit Secrets
gemini_api_key = st.secrets.get("GEMINI_API_KEY")
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
aws_region = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
s3_bucket_name = st.secrets.get("AWS_S3_BUCKET_NAME")

# Thanh điều hướng (Sidebar)
cloud_provider = st.sidebar.radio(
    "🌐 Chọn nền tảng Cloud Demo:",
    ["1. Google Cloud (Gemini AI)", "2. Amazon Web Services (AWS Native)"]
)

option = st.sidebar.selectbox(
    "🎯 Chọn loại dữ liệu xử lý:",
    ["Phân Tích Hình Ảnh", "Bóc Băng Âm Thanh / Video"]
)

st.sidebar.divider()
st.sidebar.info(
    "💡 **Gợi ý báo cáo:**\n"
    "- **Google Gemini:** Trích xuất ngữ cảnh, giải thích tự nhiên, bóc băng & tóm tắt thông minh.\n"
    "- **AWS Native:** Trích xuất nhãn/vật thể dạng metadata (JSON), tốc độ cao, tối ưu cho tự động hóa."
)

# =========================================================
# NỀN TẢNG 1: GOOGLE CLOUD (GEMINI AI)
# =========================================================
if cloud_provider == "1. Google Cloud (Gemini AI)":
    st.subheader("🟢 Google Cloud Platform - Gemini 3.6 Flash")
    
    if option == "Phân Tích Hình Ảnh":
        uploaded_file = st.file_uploader("Tải lên ảnh (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Ảnh đầu vào", use_container_width=True)
            
            user_prompt = st.text_input("Yêu cầu thêm (Tùy chọn):", placeholder="Ví dụ: Mô tả con người và hoạt động trong ảnh")
            
            if st.button("🚀 Phân tích với Gemini AI"):
                if not gemini_api_key:
                    st.error("Chưa cấu hình GEMINI_API_KEY!")
                else:
                    try:
                        with st.spinner("Gemini đang quan sát và phân tích..."):
                            client = genai.Client(api_key=gemini_api_key.strip())
                            default_prompt = "Hãy phân tích chi tiết bức ảnh này: thể loại, con người, vật thể, hành động và ngữ cảnh tổng quan bằng Tiếng Việt."
                            prompt = user_prompt if user_prompt.strip() else default_prompt
                            
                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=[image, prompt]
                            )
                            st.success("Phân tích hoàn tất!")
                            st.markdown("### 📊 Kết quả từ Gemini AI:")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"Lỗi Gemini: {e}")

    elif option == "Bóc Băng Âm Thanh / Video":
        uploaded_file = st.file_uploader("Tải lên Audio/Video", type=["mp3", "wav", "mp4", "m4a", "aac"])
        if uploaded_file:
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext in ["mp3", "wav", "m4a", "aac"]:
                st.audio(uploaded_file)
            else:
                st.video(uploaded_file)
                
            if st.button("🚀 Bóc băng toàn bộ với Gemini AI"):
                if not gemini_api_key:
                    st.error("Chưa cấu hình GEMINI_API_KEY!")
                else:
                    try:
                        with st.spinner("Gemini đang xử lý toàn bộ file âm thanh..."):
                            client = genai.Client(api_key=gemini_api_key.strip())
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                                tmp_file.write(uploaded_file.read())
                                tmp_path = tmp_file.name
                            
                            audio_file = client.files.upload(file=tmp_path)
                            prompt = "Hãy bóc băng nguyên văn 100% nội dung âm thanh này bằng Tiếng Việt hoặc ngôn ngữ gốc, sau đó tóm tắt 3 ý chính."
                            
                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=[audio_file, prompt]
                            )
                            st.success("Bóc băng hoàn tất!")
                            st.markdown("### 📝 Kết quả từ Gemini AI:")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"Lỗi xử lý Audio Gemini: {e}")

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
                if not aws_access_key or not aws_secret_key:
                    st.error("Chưa cấu hình AWS Credentials trong Secrets!")
                else:
                    try:
                        with st.spinner("AWS Rekognition đang nhận diện nhãn (Labels)..."):
                            rekognition = boto3.client(
                                'rekognition',
                                aws_access_key_id=aws_access_key.strip(),
                                aws_secret_access_key=aws_secret_key.strip(),
                                region_name=aws_region.strip()
                            )
                            
                            response = rekognition.detect_labels(
                                Image={'Bytes': image_bytes},
                                MaxLabels=12,
                                MinConfidence=70
                            )
                            
                            st.success("AWS Rekognition phân tích thành công!")
                            st.markdown("### 🏷️ Danh sách nhãn phát hiện được (Labels):")
                            
                            labels_data = []
                            for label in response['Labels']:
                                labels_data.append({
                                    "Nhãn vật thể (Label)": label['Name'],
                                    "Độ tin cậy (Confidence)": f"{label['Confidence']:.2f}%"
                                })
                            st.table(labels_data)

                    except Exception as e:
                        st.error(f"Lỗi kết nối AWS Rekognition: {e}")

    elif option == "Bóc Băng Âm Thanh / Video":
        st.info("📌 AWS Transcribe lưu trữ file vào S3 Bucket trước khi trích xuất lời nói.")
        uploaded_file = st.file_uploader("Tải lên Audio (MP3, WAV)", type=["mp3", "wav"])
        
        if uploaded_file:
            st.audio(uploaded_file)
            if st.button("🚀 Bóc băng với AWS Transcribe"):
                if not aws_access_key or not s3_bucket_name:
                    st.error("Cần cấu hình đủ AWS Keys và AWS_S3_BUCKET_NAME!")
                else:
                    try:
                        with st.spinner("1/3: Đang tải file lên AWS S3..."):
                            s3 = boto3.client(
                                's3',
                                aws_access_key_id=aws_access_key.strip(),
                                aws_secret_access_key=aws_secret_key.strip(),
                                region_name=aws_region.strip()
                            )
                            file_name = f"audio_{int(time.time())}.{uploaded_file.name.split('.')[-1]}"
                            s3.upload_fileobj(uploaded_file, s3_bucket_name, file_name)
                            file_uri = f"s3://{s3_bucket_name}/{file_name}"

                        with st.spinner("2/3: AWS Transcribe đang bóc băng..."):
                            transcribe = boto3.client(
                                'transcribe',
                                aws_access_key_id=aws_access_key.strip(),
                                aws_secret_access_key=aws_secret_key.strip(),
                                region_name=aws_region.strip()
                            )
                            job_name = f"Job_{int(time.time())}"
                            transcribe.start_transcription_job(
                                TranscriptionJobName=job_name,
                                Media={'MediaFileUri': file_uri},
                                MediaFormat=uploaded_file.name.split('.')[-1],
                                LanguageCode='en-US'
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
                            st.markdown("### 📝 Văn bản từ AWS Transcribe:")
                            st.write(text)
                        else:
                            st.error("Bóc băng trên AWS thất bại.")

                    except Exception as e:
                        st.error(f"Lỗi AWS Transcribe: {e}")
