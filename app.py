import io
import time
import uuid
import boto3
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="AWS AI Multi-Tool", layout="centered")
st.title("🤖 Ứng Dụng AI Đa Năng - AWS Cloud")

# Cấu hình AWS Keys từ Streamlit Secrets
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
region = "ap-southeast-2"
S3_BUCKET_NAME = "my-transcribe-audio-bucket-2026"  # Tên Bucket bạn vừa tạo

# Chọn chức năng
option = st.sidebar.selectbox(
    "Chọn tính năng AI",
    ["1. Nhận diện Hình ảnh (Rekognition)", "2. Nhận diện Âm thanh (Transcribe)"],
)

# ---------------------------------------------------------
# TÍNH NĂNG 1: NHẬN DIỆN HÌNH ẢNH
# ---------------------------------------------------------
if option == "1. Nhận diện Hình ảnh (Rekognition)":
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

# ---------------------------------------------------------
# TÍNH NĂNG 2: NHẬN DIỆN ÂM THANH
# ---------------------------------------------------------
elif option == "2. Nhận diện Âm thanh (Transcribe)":
    st.header("🎙️ Chuyển Giọng Nói Thành Văn Bản")
    audio_file = st.file_uploader(
        "Chọn file âm thanh", type=["mp3", "wav", "m4a"]
    )

    if audio_file:
        st.audio(audio_file)

        if st.button("Bắt đầu nhận diện giọng nói"):
            if not aws_access_key or not aws_secret_key:
                st.error("Chưa cấu hình AWS Keys!")
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
                    file_name = f"audio_{uuid.uuid4().hex}.mp3"
                    st.info("Đang tải file âm thanh lên AWS S3...")
                    s3_client.upload_fileobj(
                        audio_file, S3_BUCKET_NAME, file_name
                    )
                    file_uri = f"s3://{S3_BUCKET_NAME}/{file_name}"

                    # 2. Tạo Transcription Job
                    job_name = f"job_{uuid.uuid4().hex}"
                    st.info("Đang gửi tới AWS Transcribe AI...")
                    transcribe_client.start_transcription_job(
                        TranscriptionJobName=job_name,
                        Media={"MediaFileUri": file_uri},
                        MediaFormat="mp3",
                        LanguageCode="vi-VN",  # Nhận diện tiếng Việt
                    )

                    # 3. Chờ kết quả
                    with st.spinner("AWS Transcribe đang lắng nghe và giải mã..."):
                        while True:
                            status = transcribe_client.get_transcription_job(
                                TranscriptionJobName=job_name
                            )
                            job_status = status["TranscriptionJob"][
                                "TranscriptionJobStatus"
                            ]
                            if job_status in ["COMPLETED", "FAILED"]:
                                break
                            time.sleep(2)

                    if job_status == "COMPLETED":
                        transcript_url = status["TranscriptionJob"][
                            "Transcript"
                        ]["TranscriptFileUri"]
                        res = requests.get(transcript_url)
                        text = res.json()["results"]["transcripts"][0][
                            "transcript"
                        ]

                        st.success("Nhận diện thành công!")
                        st.subheader("📝 Văn bản trích xuất:")
                        st.write(text)
                    else:
                        st.error("Xử lý âm thanh thất bại!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
