import io
import boto3
import streamlit as st
from PIL import Image

st.set_page_config(page_title="AWS AI Multi-Tool", layout="centered")
st.title("🤖 Ứng Dụng AI Đa Năng - AWS Cloud")

# Cấu hình AWS Keys từ Streamlit Secrets
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
region = "ap-southeast-2"

# Chọn chức năng
option = st.sidebar.selectbox(
    "Chọn tính năng AI",
    ["1. Nhận diện Hình ảnh (Rekognition)", "2. Tạo Âm thanh/Giọng nói (Polly)"],
)

# ---------------------------------------------------------
# TÍNH NĂNG 1: NHẬN DIỆN HÌNH ẢNH (AWS Rekognition)
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
# TÍNH NĂNG 2: CHUYỂN VĂN BẢN THÀNH GIỌNG NÓI (AWS Polly)
# ---------------------------------------------------------
elif option == "2. Tạo Âm thanh/Giọng nói (Polly)":
    st.header("🔊 Tạo Giọng Nói AI Từ Văn Bản")
    
    text_input = st.text_area(
        "Nhập văn bản cần phát âm thanh:",
        value="Xin chào! Đây là ứng dụng Điện toán đám mây sử dụng dịch vụ AWS Polly để chuyển đổi văn bản thành giọng nói.",
        height=120,
    )

    voice_option = st.selectbox(
        "Chọn giọng đọc:",
        ["Tiếng Việt - Thi (Nữ)", "Tiếng Anh - Joanna (Nữ)", "Tiếng Anh - Matthew (Nam)"],
    )

    if st.button("Tạo file âm thanh"):
        if not text_input.strip():
            st.warning("Vui lòng nhập văn bản!")
        elif not aws_access_key or not aws_secret_key:
            st.error("Chưa cấu hình AWS Keys!")
        else:
            try:
                polly_client = boto3.client(
                    "polly",
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region,
                )

                # Cấu hình giọng đọc
                if "Thi" in voice_option:
                    voice_id = "Thi"
                    lang_code = "vi-VN"
                elif "Joanna" in voice_option:
                    voice_id = "Joanna"
                    lang_code = "en-US"
                else:
                    voice_id = "Matthew"
                    lang_code = "en-US"

                with st.spinner("AWS Polly đang tạo file âm thanh..."):
                    response = polly_client.synthesize_speech(
                        Text=text_input,
                        OutputFormat="mp3",
                        VoiceId=voice_id,
                        LanguageCode=lang_code,
                    )

                    if "AudioStream" in response:
                        audio_data = response["AudioStream"].read()
                        st.success("Tạo âm thanh thành công!")
                        st.audio(audio_data, format="audio/mp3")
            except Exception as e:
                st.error(f"Lỗi: {e}")
