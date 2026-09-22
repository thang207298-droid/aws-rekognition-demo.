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

GEMINI_MODEL_NAME = "gemini-3.6-flash"

# ==========================================
# SIDEBAR MENU
# ==========================================
st.sidebar.title("📌 Menu Chức Năng")
feature = st.sidebar.radio(
    "Chọn tính năng xử lý:",
    ["🎙️ Bóc Băng & Phân Tích Âm Thanh (Gemini AI)", "🖼️ Nhận Diện Hình Ảnh (AWS Rekognition / Gemini)"]
)

# ==========================================
# TÍNH NĂNG 1: BÓC BĂNG & PHÂN TÍCH ÂM THANH
# ==========================================
if feature == "🎙️ Bóc Băng & Phân Tích Âm Thanh (Gemini AI)":
    st.title("🎙️ Bóc Băng & Phân Tích Âm Thanh")
    st.caption("Chép lời, dịch tiếng Việt và đúc kết 1 dòng mục đích ngắn gọn.")

    uploaded_audio = st.file_uploader("Tải lên file Audio (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

    if uploaded_audio is not None:
        st.audio(uploaded_audio)
        
        if st.button("🚀 Bóc băng & Phân tích"):
            if not GEMINI_API_KEY:
                st.error("Chưa cấu hình GEMINI_API_KEY trong Secrets!")
            else:
                with st.spinner("Gemini 3.6 Flash đang phân tích..."):
                    try:
                        audio_bytes = uploaded_audio.read()
                        file_ext = uploaded_audio.name.split(".")[-1].lower()
                        mime_type = f"audio/{file_ext}" if file_ext != "mp3" else "audio/mpeg"
                        
                        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
                        
                        prompt = """
                        Hãy phân tích file âm thanh này theo cấu trúc ngắn gọn sau:

                        ### 📝 NỘI DUNG LỜI THOẠI:
                        (Liệt kê các câu thoại gốc, không đánh số thứ tự)

                        ### 🌐 BẢN DỊCH TIẾNG VIỆT:
                        (Dịch nghĩa tiếng Việt tương ứng)

                        ### 🎯 MỤC ĐÍCH:
                        (Chỉ viết ĐÚNG 1 DÒNG kết luận chung ngắn gọn nhất về mục đích của đoạn hội thoại này).
                        """
                        
                        response = model.generate_content([
                            prompt,
                            {"mime_type": mime_type, "data": audio_bytes}
                        ])
                        
                        st.success("✅ Phân tích thành công!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Lỗi xử lý âm thanh: {e}")

# ==========================================
# TÍNH NĂNG 2: PHÂN TÍCH HÌNH ẢNH
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
                            
        else:
            if st.button("🔍 Mô tả ảnh với Gemini"):
                if not GEMINI_API_KEY:
                    st.error("Chưa cấu hình GEMINI_API_KEY trong Secrets!")
                else:
                    with st.spinner("Gemini 3.6 Flash đang xem ảnh..."):
                        try:
                            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
                            
                            # Prompt đã rút gọn, đi thẳng vào ý chính và có 1 dòng kết luận chung
                            vision_prompt = """
                            Hãy phân tích hình ảnh này theo cấu trúc ngắn gọn:
                            - **Mô tả ngắn**: Liệt kê các đối tượng và chi tiết chính nổi bật trong ảnh.
                            - **Kết luận**: Viết đúng 1 dòng tổng kết ngắn gọn nhất về bản chất/nội dung của hình ảnh này.
                            """
                            
                            response = model.generate_content([
                                vision_prompt,
                                image
                            ])
                            st.success("✅ Phân tích xong!")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Lỗi Gemini Vision: {e}")
