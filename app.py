import streamlit as st
import boto3
from PIL import Image
import io
import google.generativeai as genai

# ==========================================
# CẤU HÌNH TRANG VÀ API KEYS TỪ SECRETS
# ==========================================
st.set_page_config(
    page_title="AI Nhận Diện Hình Ảnh Và Âm Thanh",
    page_icon="☁️",
    layout="wide"
)

# Lấy cấu hình từ Streamlit Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
AWS_ACCESS_KEY_ID = st.secrets.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = st.secrets.get("AWS_SECRET_ACCESS_KEY", "")
AWS_DEFAULT_REGION = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Sidebar chọn nền tảng
st.sidebar.title("Chọn nền tảng Cloud Demo:")
option = st.sidebar.radio(
    "",
    ["1. Google Cloud (Gemini AI)", "2. Amazon Web Services (AWS Native)"],
    index=1
)

st.title("☁️ AI Nhận Diện Hình Ảnh Và Âm Thanh")

if option == "2. Amazon Web Services (AWS Native)":
    st.header("🟠 Amazon Web Services (AWS Rekognition & Gemini Audio)")
    
    # Chọn loại xử lý
    task_type = st.sidebar.selectbox(
        "Chọn loại dữ liệu xử lý:",
        ["Bóc Bằng Âm Thanh / Video", "Nhận Diện Hình Ảnh"]
    )
    
    if task_type == "Bóc Bằng Âm Thanh / Video":
        st.info("📌 Hệ thống sử dụng Gemini AI để chuyển lời nói thành văn bản tiếng Việt chính xác cao.")
        
        uploaded_audio = st.file_uploader("Tải lên Audio (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
        
        if uploaded_audio is not None:
            st.audio(uploaded_audio)
            
            if st.button("🚀 Bóc băng với Gemini AI"):
                if not GEMINI_API_KEY:
                    st.error("Chưa cấu hình GEMINI_API_KEY trong Secrets!")
                else:
                    with st.spinner("Gemini đang lắng nghe và trích xuất lời nói..."):
                        try:
                            audio_bytes = uploaded_audio.read()
                            file_ext = uploaded_audio.name.split(".")[-1].lower()
                            mime_type = f"audio/{file_ext}" if file_ext != "mp3" else "audio/mpeg"
                            
                            # Khởi tạo Gemini Flash
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            
                            response = model.generate_content([
                                "Hãy chép lại chính xác toàn bộ nội dung lời nói trong file âm thanh này sang văn bản tiếng Việt.",
                                {"mime_type": mime_type, "data": audio_bytes}
                            ])
                            
                            st.success("✅ Bóc băng thành công!")
                            st.subheader("Nội dung bóc băng:")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"Lỗi xử lý âm thanh: {e}")

    elif task_type == "Nhận Diện Hình Ảnh":
        st.info("📌 Phân tích và phát hiện nhãn đối tượng bằng AWS Rekognition.")
        
        uploaded_img = st.file_uploader("Tải lên Hình ảnh (JPG, PNG)", type=["jpg", "jpeg", "png"])
        
        if uploaded_img is not None:
            image = Image.open(uploaded_img)
            st.image(image, caption="Hình ảnh đã tải lên", use_container_width=True)
            
            if st.button("🔍 Phân tích ảnh với AWS Rekognition"):
                if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY):
                    st.error("Chưa cấu hình AWS Credentials trong Secrets!")
                else:
                    with st.spinner("AWS Rekognition đang quét ảnh..."):
                        try:
                            rek_client = boto3.client(
                                'rekognition',
                                aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                region_name=AWS_DEFAULT_REGION
                            )
                            
                            buffer = io.BytesIO()
                            image.save(buffer, format=image.format if image.format else "JPEG")
                            img_bytes = buffer.getvalue()
                            
                            res = rek_client.detect_labels(
                                Image={'Bytes': img_bytes},
                                MaxLabels=10,
                                MinConfidence=70
                            )
                            
                            st.success("✅ Phân tích xong!")
                            st.subheader("Các nhãn đối tượng phát hiện được:")
                            for label in res['Labels']:
                                st.write(f"- **{label['Name']}**: {label['Confidence']:.2f}%")
                        except Exception as e:
                            st.error(f"Lỗi AWS Rekognition: {e}")

else:
    st.header("🔵 Google Cloud (Gemini AI)")
    st.write("Phiên bản hỗ trợ hoàn toàn bằng Gemini Multimodal AI.")
