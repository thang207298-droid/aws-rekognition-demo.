import streamlit as st
from PIL import Image
import google.generativeai as genai

# ==========================================
# CẤU HÌNH TRANG & SECRETS
# ==========================================
st.set_page_config(
    page_title="AI Application - Vision & Audio",
    page_icon="🤖",
    layout="wide"
)

# Đọc danh sách các API Key Gemini từ secrets.toml
GEMINI_API_KEYS = st.secrets.get("GEMINI_API_KEYS", [])
if not GEMINI_API_KEYS:
    single_key = st.secrets.get("GEMINI_KEY", "")
    GEMINI_API_KEYS = [single_key] if single_key else []

GEMINI_MODEL_NAME = "gemini-3.6-flash"

# Hàm gọi Gemini tự động xoay vòng key khi hết quota (429)
def call_gemini_with_fallback(prompt_content):
    if not GEMINI_API_KEYS:
        raise Exception("Chưa cấu hình bất kỳ GEMINI_API_KEYS nào trong secrets.toml!")
    
    last_exception = None
    for idx, key in enumerate(GEMINI_API_KEYS):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            response = model.generate_content(prompt_content)
            return response.text 
        except Exception as e:
            last_exception = e
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                continue
            else:
                raise e
                
    raise Exception(f"Tất cả các API Key đều đã cạn kiệt hạn mức hoặc gặp lỗi: {last_exception}")

# ==========================================
# SIDEBAR MENU
# ==========================================
st.sidebar.title("📌 Menu Chức Năng")
feature = st.sidebar.radio(
    "Chọn tính năng xử lý:",
    ["🎙️ AI Nhận Diện Âm Thanh", "🖼️ Nhận Diện Hình Ảnh (Gemini Vision)"]
)

# ==========================================
# TÍNH NĂNG 1: AI NHẬN DIỆN ÂM THANH
# ==========================================
if feature == "🎙️ AI Nhận Diện Âm Thanh":
    st.title("🎙️ AI Nhận Diện Âm Thanh")
    st.caption("Chép lời, dịch tiếng Việt và đúc kết 1 dòng mục đích ngắn gọn.")

    uploaded_audio = st.file_uploader("Tải lên file Audio (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

    if uploaded_audio is not None:
        st.audio(uploaded_audio)
        
        if st.button("🚀 Bóc băng & Phân tích"):
            if not GEMINI_API_KEYS:
                st.error("Chưa cấu hình API Key trong Secrets!")
            else:
                with st.spinner("Đang xử lý âm thanh..."):
                    try:
                        audio_bytes = uploaded_audio.read()
                        file_ext = uploaded_audio.name.split(".")[-1].lower()
                        mime_type = f"audio/{file_ext}" if file_ext != "mp3" else "audio/mpeg"
                        
                        prompt = """
                        Hãy phân tích file âm thanh này theo cấu trúc ngắn gọn sau:

                        ### 📝 NỘI DUNG LỜI THOẠI:
                        (Liệt kê các câu thoại gốc, không đánh số thứ tự)

                        ### 🌐 BẢN DỊCH TIẾNG VIỆT:
                        (Dịch nghĩa tiếng Việt tương ứng)

                        ### 🎯 MỤC ĐÍCH:
                        (Chỉ viết ĐÚNG 1 DÒNG kết luận chung ngắn gọn nhất về mục đích của đoạn hội thoại này).
                        """
                        
                        result_text = call_gemini_with_fallback([
                            prompt,
                            {"mime_type": mime_type, "data": audio_bytes}
                        ])
                        
                        st.success("✅ Phân tích thành công!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Lỗi xử lý âm thanh: {e}")

# ==========================================
# TÍNH NĂNG 2: PHÂN TÍCH HÌNH ẢNH (GEMINI VISION)
# ==========================================
elif feature == "🖼️ Nhận Diện Hình Ảnh (Gemini Vision)":
    st.title("🖼️ Phân Tích & Nhận Diện Hình Ảnh")
    st.caption("Sử dụng Gemini Vision phân tích trực tiếp hình ảnh.")
    
    uploaded_img = st.file_uploader("Tải lên Hình ảnh (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_img is not None:
        image = Image.open(uploaded_img)
        st.image(image, caption="Hình ảnh đã tải lên", use_container_width=True)
        
        if st.button("🔍 Phân tích ảnh với Gemini"):
            if not GEMINI_API_KEYS:
                st.error("Chưa cấu hình API Key trong Secrets!")
            else:
                with st.spinner("Gemini đang phân tích ảnh..."):
                    try:
                        vision_prompt = """
                        Hãy phân tích hình ảnh này theo cấu trúc ngắn gọn:
                        - **Mô tả ngắn**: Liệt kê các đối tượng và chi tiết chính nổi bật trong ảnh.
                        - **Kết luận**: Viết đúng 1 dòng tổng kết ngắn gọn nhất về bản chất/nội dung của hình ảnh này.
                        """
                        
                        result_text = call_gemini_with_fallback([vision_prompt, image])
                        st.success("✅ Phân tích xong!")
                        st.markdown(result_text)
                    except Exception as e:
                        st.error(f"Lỗi phân tích ảnh: {e}")
