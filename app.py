import io
import tempfile
import boto3
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from PIL import Image

st.set_page_config(page_title="AI Multi-Tool", layout="centered")
st.title("🤖 Ứng Dụng AI - Bóc Băng & Phân Tích Đa Phương Tiện")

# Cấu hình AWS Keys từ Streamlit Secrets
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
region = "us-east-1"

option = st.sidebar.selectbox(
    "Chọn tính năng AI",
    [
        "1. Phân Tích Audio/Video (AI Speech Recognition)",
        "2. Nhận diện Hình ảnh (AWS Rekognition)",
    ],
)

# ---------------------------------------------------------
# TÍNH NĂNG 1: BÓC BẰNG AUDIO / VIDEO
# ---------------------------------------------------------
if option == "1. Phân Tích Audio/Video (AI Speech Recognition)":
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
                with st.spinner("Đang chuyển đổi định dạng và bóc băng âm thanh..."):
                    # Lưu file tạm
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name

                    # Convert audio sang WAV chuẩn PCM cho SpeechRecognition
                    audio_segment = AudioSegment.from_file(tmp_path)
                    wav_path = tmp_path + ".wav"
                    audio_segment.export(wav_path, format="wav")

                    # Bóc băng giọng nói
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        audio_data = recognizer.record(source)
                        
                        # Tự động nhận diện giọng nói tiếng Anh
                        text_output = recognizer.recognize_google(audio_data, language="en-US")

                st.success("Xử lý hoàn tất!")
                st.subheader("📝 Văn bản trích xuất nguyên bản:")
                if text_output:
                    st.write(text_output)

                    st.divider()
                    st.subheader("🔍 Kết quả phân tích âm thanh:")
                    word_count = len(text_output.split())
                    st.write(f"• **Tổng số từ chép được:** {word_count} từ")
                    st.write("• **Ngôn ngữ xử lý:** Tiếng Anh (en-US)")

                else:
                    st.write("Không nhận diện được nội dung thoại trong file.")

            except sr.UnknownValueError:
                st.error("Không thể nhận diện âm thanh trong file. Hãy kiểm tra lại micro hoặc độ rõ của giọng nói.")
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
