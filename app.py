import io
import tempfile
import boto3
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from PIL import Image
from google import genai

st.set_page_config(page_title="AI Multi-Tool", layout="centered")
st.title("🤖 Ứng Dụng AI - Nhận Diện Hình Ảnh & Bóc Băng")

# Lấy Keys từ Secrets
aws_access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
aws_secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
region = "us-east-1"
gemini_api_key = st.secrets.get("GEMINI_API_KEY")

option = st.sidebar.selectbox(
    "Chọn tính năng AI",
    [
        "1. Phân Tích Hình Ảnh Đa Năng (Gemini Vision)",
        "2. Bóc Băng Audio/Video (Speech Recognition)",
        "3. Nhận diện Cơ bản (AWS Rekognition)",
    ],
)

# ---------------------------------------------------------
# TÍNH NĂNG 1: PHÂN TÍCH HÌNH ẢNH ĐA NĂNG (GEMINI VISION)
# ---------------------------------------------------------
if option == "1. Phân Tích Hình Ảnh Đa Năng (Gemini Vision)":
    st.header("🖼️ Phân Tích Bất Kỳ Bức Ảnh Nào")
    st.write("Tải lên ảnh bầu trời, con người, đồ vật, phong cảnh... AI sẽ phân tích chi tiết bằng Tiếng Việt.")

    uploaded_file = st.file_uploader(
        "Chọn ảnh bất kỳ để phân tích", type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã tải lên", use_container_width=True)

        user_prompt = st.text_input(
            "Yêu cầu riêng cho AI (Tùy chọn):",
            placeholder="Ví dụ: Bầu trời này thời tiết ra sao? Hoặc: Đồ vật này dùng làm gì?"
        )

        if st.button("🚀 Bắt đầu phân tích toàn diện"):
            if not gemini_api_key:
                st.error("Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets!")
            else:
                try:
                    with st.spinner("AI đang quan sát và phân tích toàn bộ bức ảnh..."):
                        client = genai.Client(api_key=gemini_api_key)

                        default_prompt = (
                            "Hãy quan sát kỹ bức ảnh này và phân tích thật chi tiết bằng Tiếng Việt theo các mục sau:\n"
                            "1. **Chủ đề chính & Tổng quan:** Bức ảnh chụp gì? (Bầu trời, con người, đồ vật, phong cảnh, thiết kế đồ họa...)\n"
                            "2. **Phân tích con người (nếu có):** Số lượng, độ tuổi ước tính, cảm xúc, hành động, trang phục.\n"
                            "3. **Phân tích đối tượng / Đồ vật / Bầu trời:** Chi tiết các đối tượng xuất hiện, thời tiết/bầu trời (nếu có), màu sắc chủ đạo.\n"
                            "4. **Nhận xét & Ngữ cảnh:** Môi trường xung quanh, không gian hoặc công dụng của đối tượng."
                        )

                        prompt_to_use = user_prompt if user_prompt.strip() else default_prompt

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[image, prompt_to_use]
                        )

                        st.success("Phân tích hoàn tất!")
                        st.markdown("### 📊 Kết quả phân tích từ AI:")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Lỗi phân tích hình ảnh: {e}")

# ---------------------------------------------------------
# TÍNH NĂNG 2: BÓC BẰNG AUDIO / VIDEO
# ---------------------------------------------------------
elif option == "2. Bóc Băng Audio/Video (Speech Recognition)":
    st.header("🎙️ Bóc Băng Âm Thanh / Video")

    uploaded_file = st.file_uploader(
        "Tải lên file Audio hoặc Video",
        type=["mp3", "mp4", "wav", "m4a", "aac", "flac", "ogg", "mov", "avi", "mkv", "webm"],
    )

    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()

        if ext in ["mp3", "wav", "m4a", "aac", "flac", "ogg"]:
            st.audio(uploaded_file)
        else:
            st.video(uploaded_file)

        if st.button("Bắt đầu bóc băng"):
            try:
                with st.spinner("Đang xử lý âm thanh..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name

                    audio_segment = AudioSegment.from_file(tmp_path)
                    wav_path = tmp_path + ".wav"
                    audio_segment.export(wav_path, format="wav")

                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        audio_data = recognizer.record(source)
                        text_output = recognizer.recognize_google(audio_data, language="en-US")

                st.success("Xử lý hoàn tất!")
                st.subheader("📝 Văn bản trích xuất nguyên bản:")
                if text_output:
                    st.write(text_output)
                    st.divider()
                    word_count = len(text_output.split())
                    st.write(f"• **Tổng số từ:** {word_count} từ")
                else:
                    st.write("Không nhận diện được âm thanh.")

            except Exception as e:
                st.error(f"Lỗi bóc băng: {e}")

# ---------------------------------------------------------
# TÍNH NĂNG 3: NHẬN DIỆN CƠ BẢN (AWS REKOGNITION)
# ---------------------------------------------------------
elif option == "3. Nhận diện Cơ bản (AWS Rekognition)":
    st.header("🖼️ Phân Tích Nhãn Bằng AWS Rekognition")
    uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã tải lên", use_container_width=True)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format if image.format else "JPEG")
        img_bytes = img_byte_arr.getvalue()

        if st.button("Phân tích AWS"):
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
                    response_labels = client.detect_labels(
                        Image={"Bytes": img_bytes},
                        MaxLabels=10,
                        MinConfidence=60,
                    )
                    st.subheader("📌 Vật thể & Nhãn phát hiện:")
                    for label in response_labels.get("Labels", []):
                        st.write(f"• **{label['Name']}**: {label['Confidence']:.1f}%")

                except Exception as e:
                    st.error(f"Lỗi AWS: {e}")
