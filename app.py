import streamlit as st
import boto3
from PIL import Image
import io
import google.generativeai as genai

# ==========================================
# CẤU HÌNH TRANG & SECRETS
# ==========================================
st.set_page_config(
    page_title="AI Application - Vision & Audio",
    page_icon="🤖",
    layout="wide"
)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
AWS_ACCESS_KEY_ID = st.secrets.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = st.secrets.get("AWS_SECRET_ACCESS_KEY", "")
AWS_DEFAULT_REGION = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# SIDEBAR DI CHUYỂN
# ==========================================
st.sidebar.title("📌 Menu Chức Năng")
feature = st.sidebar.radio(
    "Chọn tính năng xử lý:",
    ["🎙️ Bóc Băng Âm Thanh (Gemini AI)", "🖼️ Nhận Diện Hình Ảnh (AWS Rekognition / Gemini)"]
)

# ==========================================
# TÍNH NĂNG 1: BÓC BĂNG ÂM THANH (DÙNG GEMINI)
# ==========================================
if feature == "🎙️ Bóc Băng Âm Thanh (Gemini AI)":
    st.title("🎙️ Bóc Băng Âm Thanh / Video")
    st.caption("Sử dụng mô hình Gemini Flash AI hỗ trợ nhận diện tiếng Việt cực chính xác.")

    uploaded_audio = st.file_uploader("Tải lên file Audio (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

    if uploaded_audio is not None:
        st.audio(uploaded_audio)
        
        if st.button("🚀 Bóc băng lời nói"):
            if not GEMINI_API_KEY:
                st.error("Chưa cấu hình GEMINI_API_KEY trong Secrets!")
            else:
                with st.spinner("Gemini đang lắng nghe và trích xuất lời nói..."):
                    try:
                        audio_bytes = uploaded_audio.read()
                        file_ext = uploaded_audio.name.split(".")[-1].lower()
                        mime_type = f"audio/{file_ext}" if file_ext != "mp3" else "audio/mpeg"
                        
                        # Sử dụng Gemini Flash (tự động điều hướng bản Flash mới nhất)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        
                        response = model.generate_content([
                            "Hãy chép lại chính xác toàn bộ nội dung lời nói trong file âm thanh này sang văn bản tiếng Việt.",
                            {"mime_type": mime_type, "data": audio_bytes}
                        ])
                        
                        st.success("✅ Bóc băng thành công!")
                        st.text_area("Văn bản bóc băng:", value=response.text, height=250)
                    except Exception as e:
                        st.error(f"Lỗi xử lý âm thanh: {e}")

# ==========================================
# TÍNH NĂNG 2: PHÂN TÍCH HÌNH ẢNH (AWS REKOGNITION)
# ==========================================
elif feature == "🖼️ Nhận Diện Hình Ảnh (AWS Rekognition / Gemini)":
    st.title("🖼️ Phân Tích & Nhận Diện Hình Ảnh")
    
    vision_engine = st.radio(
        "Chọn Engine xử lý ảnh:",
        ["Amazon Web Services (AWS Rekognition)", "Google Cloud (Gemini Vision)"],
        horizontal=True
    )
    
    uploaded_img = st.file_uploader("Tải lên Hình ảnh (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_img is not None:
        image = Image.open(uploaded_img)
        st.image(image, caption="Hình ảnh đã tải lên", use_container_width=True)
        
        # Nhánh AWS Rekognition
        if vision_engine == "Amazon Web Services (AWS Rekognition)":
            if st.button("🔍 Phân tích Nhãn với AWS"):
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
                            
                            st.success("✅ Phân tích nhãn thành công!")
                            st.write("**Các đối tượng phát hiện được:**")
                            for label in res['Labels']:
                                st.write(f"- **{label['Name']}**: {label['Confidence']:.2f}%")
                        except Exception as e:
                            st.error(f"Lỗi AWS Rekognition: {e}")
                            
        # Nhánh Gemini AI
        else:
            if st.button("🔍 Mô tả ảnh với Gemini"):
                if not GEMINI_API_KEY:
                    st.error("Chưa cấu hình GEMINI_API_KEY trong Secrets!")
                else:
                    with st.spinner("Gemini đang xem ảnh..."):
                        try:
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            response = model.generate_content([
                                "Hãy mô tả chi tiết các đối tượng và bối cảnh trong hình ảnh này bằng tiếng Việt.",
                                image
                            ])
                            st.success("✅ Phân tích xong!")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"Lỗi Gemini Vision: {e}")
