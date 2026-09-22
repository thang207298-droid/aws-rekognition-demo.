import streamlit as st
import boto3
from PIL import Image
import io
import google.generativeai as genai

# ==========================================
# 1. CẤU HÌNH TRANG VÀ API KEYS
# ==========================================
st.set_page_config(
    page_title="AI Analysis Dashboard - AWS & Gemini",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Multimodal Assistant")
st.write("Xử lý Hình ảnh bằng **AWS Rekognition** | Bóc băng Âm thanh bằng **Gemini Flash API**")

# Cấu hình Gemini API
# Bạn có thể lưu key trong .streamlit/secrets.toml hoặc nhập trực tiếp trên Sidebar
with st.sidebar:
    st.header("🔑 Cấu hình API Keys")
    gemini_key = st.text_input("Gemini API Key", type="password", value=st.secrets.get("GEMINI_API_KEY", ""))
    aws_access_key = st.text_input("AWS Access Key ID", type="password", value=st.secrets.get("AWS_ACCESS_KEY_ID", ""))
    aws_secret_key = st.text_input("AWS Secret Access Key", type="password", value=st.secrets.get("AWS_SECRET_ACCESS_KEY", ""))
    aws_region = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "ap-southeast-1"], index=0)

    if gemini_key:
        genai.configure(api_key=gemini_key)

# Khởi tạo boto3 client cho AWS Rekognition
def get_rekognition_client():
    if aws_access_key and aws_secret_key:
        return boto3.client(
            'rekognition',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
    return None

# ==========================================
# 2. CHỨC NĂNG 1: BÓC BĂNG ÂM THANH (GEMINI FLASH)
# ==========================================
st.header("🎙️ 1. Chép lời từ File Âm thanh (Gemini Audio Transcribe)")

audio_file = st.file_uploader("Tải lên file âm thanh (MP3, WAV, M4A, OGG)", type=["mp3", "wav", "m4a", "ogg"])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("🚀 Bóc băng âm thanh với Gemini"):
        if not gemini_key:
            st.error("Vui lòng nhập Gemini API Key ở thanh bên trái!")
        else:
            with st.spinner("Gemini đang lắng nghe và bóc băng..."):
                try:
                    # Đọc bytes từ file âm thanh
                    audio_bytes = audio_file.read()
                    file_ext = audio_file.name.split(".")[-1].lower()
                    mime_type = f"audio/{file_ext}" if file_ext != "mp3" else "audio/mpeg"

                    # Dùng model Gemini Flash (Tự động nhận diện bản 2.5/3.6 Flash mới nhất)
                    model = genai.GenerativeModel("gemini-2.5-flash")

                    # Gửi prompt kèm file audio đến Gemini
                    response = model.generate_content([
                        "Hãy chép lại chính xác toàn bộ lời nói trong file âm thanh này sang văn bản tiếng Việt.",
                        {"mime_type": mime_type, "data": audio_bytes}
                    ])

                    st.success("✅ Hoàn thành bóc băng!")
                    st.text_area("Kết quả Văn bản (Transcript):", value=response.text, height=200)

                except Exception as e:
                    st.error(f"Lỗi khi xử lý âm thanh: {e}")

st.divider()

# ==========================================
# 3. CHỨC NĂNG 2: PHÂN TÍCH HÌNH ẢNH (AWS REKOGNITION + GEMINI)
# ==========================================
st.header("🖼️ 2. Phân tích Hình ảnh (AWS Rekognition & Gemini)")

image_file = st.file_uploader("Tải lên hình ảnh (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if image_file is not None:
    image = Image.open(image_file)
    st.image(image, caption="Ảnh đã tải lên", use_container_width=True)

    col1, col2 = st.columns(2)

    # --- NHÁNH 1: DÙNG AWS REKOGNITION ---
    with col1:
        st.subheader("🟠 AWS Rekognition")
        if st.button("Phân tích Nhãn (Labels) qua AWS"):
            rek_client = get_rekognition_client()
            if not rek_client:
                st.error("Vui lòng nhập đầy đủ AWS Credentials ở thanh bên!")
            else:
                with st.spinner("AWS đang quét ảnh..."):
                    try:
                        # Chuyển ảnh PIL thành Bytes
                        buffer = io.BytesIO()
                        image.save(buffer, format=image.format if image.format else "JPEG")
                        img_bytes = buffer.getvalue()

                        # Gọi dịch vụ AWS Rekognition detect_labels
                        response = rek_client.detect_labels(
                            Image={'Bytes': img_bytes},
                            MaxLabels=10,
                            MinConfidence=70
                        )

                        st.write("**Các đối tượng phát hiện được:**")
                        for label in response['Labels']:
                            st.write(f"- **{label['Name']}**: {label['Confidence']:.2f}%")

                    except Exception as e:
                        st.error(f"Lỗi AWS Rekognition: {e}")

    # --- NHÁNH 2: DÙNG GEMINI CHO HÌNH ẢNH ---
    with col2:
        st.subheader("🔵 Gemini Flash Vision")
        if st.button("Mô tả ảnh chi tiết qua Gemini"):
            if not gemini_key:
                st.error("Vui lòng nhập Gemini API Key!")
            else:
                with st.spinner("Gemini đang xem ảnh..."):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        response = model.generate_content([
                            "Hãy mô tả chi tiết nội dung bức ảnh này bằng tiếng Việt.",
                            image
                        ])

                        st.write("**Mô tả chi tiết:**")
                        st.write(response.text)

                    except Exception as e:
                        st.error(f"Lỗi Gemini Vision: {e}")
