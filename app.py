import io
import json
import time
import uuid
import boto3
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="AWS AI Multi-Tool", layout="centered")
st.title("🤖 AWS AI - Chuyển Đa Phương Tiện Thành Văn Bản & Phân Tích")

# Cấu hình AWS Keys từ Streamlit Secrets
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
region = "us-east-1"  # Khuyên dùng us-east-1 để hỗ trợ tốt nhất các dịch vụ AI

option = st.sidebar.selectbox(
    "Chọn tính năng AI",
    ["1. Phân tích Audio/Video (Transcribe)", "2. Nhận diện Hình ảnh (Rekognition)"],
)

# ---------------------------------------------------------
# TÍNH NĂNG 1: BÓC BẰNG AUDIO / VIDEO (AWS TRANSCRIBE BATCH)
# ---------------------------------------------------------
if option == "1. Phân tích Audio/Video (Transcribe)":
    st.header("🎙️ Bóc Băng File Âm Thanh & Video")
    
    s3_bucket_name = st.text_input("Nhập tên S3 Bucket của bạn:", value="")
    
    # Bổ sung đầy đủ các đuôi file âm thanh & video
    uploaded_file = st.file_uploader(
        "Tải lên file Audio hoặc Video", 
        type=["mp3", "mp4", "wav", "m4a", "aac", "flac", "ogg", "mov", "avi", "mkv", "webm"]
    )

    if uploaded_file and s3_bucket_name:
        ext = uploaded_file.name.split(".")[-1].lower()
        
        # Xem trước file media
        if ext in ["mp3", "wav", "m4a", "aac", "flac", "ogg"]:
            st.audio(uploaded_file)
        else:
            st.video(uploaded_file)

        if st.button("Bắt đầu xử lý bằng AWS AI"):
            if not aws_access_key or not aws_secret_key:
                st.error("Chưa cấu hình AWS Keys trong Streamlit Secrets!")
            else:
                try:
                    s3_client = boto3.client(
                        "s3",
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=region,
                    )
                    transcribe_client = boto3.client(
                        "transcribe",
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=region,
                    )

                    # 1. Upload file lên S3
                    file_name = f"uploads/{uuid.uuid4()}_{uploaded_file.name}"
                    with st.spinner("1/3. Đang tải file lên AWS S3..."):
                        s3_client.upload_fileobj(uploaded_file, s3_bucket_name, file_name)
                    
                    file_uri = f"s3://{s3_bucket_name}/{file_name}"
                    job_name = f"transcribe_job_{int(time.time())}"

                    # Chuẩn hóa định dạng MediaFormat cho AWS Transcribe
                    media_format_map = {
                        "mp3": "mp3", "mp4": "mp4", "wav": "wav", "flac": "flac", 
                        "ogg": "ogg", "webm": "webm", "m4a": "mp4", "aac": "mp4", 
                        "mov": "mp4", "avi": "mp4", "mkv": "mp4"
                    }
                    media_format = media_format_map.get(ext, "mp4")

                    # 2. Gửi Job bóc băng cho AWS Transcribe
                    with st.spinner("2/3. AWS Transcribe đang phân tích và chuyển file thành văn bản..."):
                        transcribe_client.start_transcription_job(
                            TranscriptionJobName=job_name,
                            Media={"MediaFileUri": file_uri},
                            MediaFormat=media_format,
                            LanguageCode="vi-VN",  # Mặc định tiếng Việt (Đổi thành "en-US" nếu file tiếng Anh)
                        )

                        # Vòng lặp chờ AWS xử lý hoàn tất
                        while True:
                            status = transcribe_client.get_transcription_job(
                                TranscriptionJobName=job_name
                            )
                            job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]
                            if job_status in ["COMPLETED", "FAILED"]:
                                break
                            time.sleep(3)

                    # 3. Lấy kết quả văn bản
                    if job_status == "COMPLETED":
                        transcript_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                        response = requests.get(transcript_uri)
                        data = response.json()
                        transcript_text = data["results"]["transcripts"][0]["transcript"]

                        st.success("3/3. Xử lý hoàn tất!")
                        st.subheader("📝 Văn bản trích xuất từ AWS Transcribe:")
                        st.write(transcript_text if transcript_text else "Không nhận diện được nội dung thoại.")
                    else:
                        st.error("Không thể hoàn tất tiến trình phân tích âm thanh trên AWS.")

                except Exception as e:
                    st.error(f"Lỗi hệ thống AWS: {e}")

# ---------------------------------------------------------
# TÍNH NĂNG 2: NHẬN DIỆN HÌNH ẢNH (AWS REKOGNITION)
# ---------------------------------------------------------
elif option == "2. Nhận diện Hình ảnh (Rekognition)":
    st.header("🖼️ Phân Tích & Nhận Diện Hình Ảnh")
    uploaded_file = st.file_uploader(
        "Chọn ảnh để phân tích", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã chọn", use_container_width=True)

        img_byte_arr = io.BytesIO()
        image.save(
            img_byte_arr,
            format=image.format if image.format else "JPEG",
        )
        img_bytes = img_byte_arr.getvalue()

        if st.button("Phân tích ảnh ngay"):
            if not aws_access_key or not aws_secret_key:
                st.error("Chưa cấu hình AWS Keys!")
            else:
                try:
                    client = boto3.client(
                        "rekognition",
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=region,
                    )
                    # Detect Labels
                    response_labels = client.detect_labels(
                        Image={"Bytes": img_bytes},
                        MaxLabels=10,
                        MinConfidence=70,
                    )
                    st.subheader("📌 Vật thể & Nhãn phát hiện:")
                    for label in response_labels["Labels"]:
                        st.write(
                            f"• **{label['Name']}**: {label['Confidence']:.1f}%"
                        )

                    # Detect Faces
                    response_faces = client.detect_faces(
                        Image={"Bytes": img_bytes}, Attributes=["ALL"]
                    )
                    faces = response_faces["FaceDetails"]
                    if faces:
                        st.divider()
                        st.subheader(f"👤 Chi tiết khuôn mặt ({len(faces)} người):")
                        for idx, face in enumerate(faces):
                            st.write(
                                f"**Người {idx+1}:** Độ tuổi khoảng {face['AgeRange']['Low']} - {face['AgeRange']['High']} | Cảm xúc: {face['Emotions'][0]['Type']}"
                            )
                except Exception as e:
                    st.error(f"Lỗi: {e}")
