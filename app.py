import io
import tempfile
import boto3
import streamlit as st
import whisper
from PIL import Image

st.set_page_config(page_title="AI Multi-Tool", layout="centered")
st.title("🤖 Ứng Dụng AI - Bóc Băng & Phân Tích Đa Phương Tiện")

# Cấu hình AWS Keys từ Streamlit Secrets
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
region = "us-east-1"


@st.cache_resource
def load_whisper_model():
    # Sử dụng mô hình small để nghe chính xác nội dung dài
    return whisper.load_model("small")


option = st.sidebar.selectbox(
    "Chọn tính năng AI",
    [
        "1. Phân Tích Audio/Video (Whisper AI)",
        "2. Nhận diện Hình ảnh (AWS Rekognition)",
    ],
)

# ---------------------------------------------------------
# TÍNH NĂNG 1: BÓC BĂNG & PHÂN TÍCH AUDIO / VIDEO
# ---------------------------------------------------------
if option == "1. Phân Tích Audio/Video (Whisper AI)":
    st.header("🎙️ Bóc Băng Âm Thanh / Video")

    uploaded_file = st.file_uploader(
        "Tải lên file Audio hoặc Video",
        type=[
            "mp3",
            "mp4",
            "wav",
            "m4a",
            "aac",
            "flac",
            "ogg",
            "mov",
            "avi",
            "mkv",
            "webm",
        ],
    )

    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()

        if ext in ["mp3", "wav", "m4a", "aac", "flac", "ogg"]:
            st.audio(uploaded_file)
        else:
            st.video(uploaded_file)

        if st.button("Bắt đầu bóc băng & Phân tích"):
            try:
                with st.spinner("1/2. Đang tải mô hình AI Whisper (Small)..."):
                    model = load_whisper_model()

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{ext}"
                ) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                with st.spinner("2/2. AI đang bóc băng toàn bộ âm thanh..."):
                    # Tự động nhận diện ngôn ngữ gốc, không dịch thuật, giữ nguyên bản
                    result = model.transcribe(
                        tmp_path,
                        task="transcribe",
                        fp16=False,
                        temperature=0.0
                    )

                text_output = result["text"].strip()

                st.success("Xử lý hoàn tất!")
                st.subheader("📝 1. Văn bản trích xuất nguyên bản:")
                if text_output:
                    st.write(text_output)

                    # PHẦN PHÂN TÍCH CHỈ SỐ NỘI DUNG
                    st.divider()
                    st.subheader("🔍 2. Kết quả phân tích âm thanh:")
                    
                    word_count = len(text_output.split())
                    st.write(f"• **Tổng số từ chép được:** {word_count} từ")
                    
                    detected_lang = result.get("language", "Không xác định").upper()
                    st.write(f"• **Ngôn ngữ AI nhận diện:** {detected_lang}")

                else:
                    st.write("Không nhận diện được nội dung thoại trong file.")

            except Exception as e:
                st.error(f"Lỗi xử lý: {e}")

# ---------------------------------------------------------
# TÍNH NĂNG 2: NHẬN DIỆN HÌNH ẢNH (AWS REKOGNITION)
# ---------------------------------------------------------
elif option == "2. Nhận diện Hình ảnh (AWS Rekognition)":
    st.header("🖼️ Phân Tích & Nhận Diện Hình Ảnh (AWS)")
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
                        st.subheader(
                            f"👤 Chi tiết khuôn mặt ({len(faces)} người):"
                        )
                        for idx, face in enumerate(faces):
                            st.write(
                                f"**Người {idx+1}:** Độ tuổi khoảng {face['AgeRange']['Low']} - {face['AgeRange']['High']} | Cảm xúc: {face['Emotions'][0]['Type']}"
                            )
                except Exception as e:
                    st.error(f"Lỗi AWS Rekognition: {e}")
