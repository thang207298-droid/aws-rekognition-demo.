import io
import tempfile
import streamlit as st
from PIL import Image
from google import genai

# Cấu hình giao diện trang web
st.set_page_config(page_title="AI Multi-Tool", layout="centered")
st.title("🤖 Ứng Dụng AI - Phân Tích Hình Ảnh & Âm Thanh")

# Lấy Gemini API Key từ Secrets
gemini_api_key = st.secrets.get("GEMINI_API_KEY")

# Menu chọn tính năng
option = st.sidebar.selectbox(
    "Select AI Feature / Chọn tính năng",
    [
        "1. Phân Tích Hình Ảnh Toàn Diện (Vision AI)",
        "2. Bóc Băng & Phân Tích Âm Thanh/Video (Audio AI)",
    ],
)

# =========================================================
# TÍNH NĂNG 1: PHÂN TÍCH HÌNH ẢNH TOÀN DIỆN
# =========================================================
if option == "1. Phân Tích Hình Ảnh Toàn Diện (Vision AI)":
    st.header("🖼️ Phân Tích & Nhận Diện Hình Ảnh")
    st.write("Hệ thống tự động nhận diện loại ảnh (Bài tập/Toán học, Phong cảnh, Con người, Đồ vật, Văn bản...) và phân tích chi tiết.")

    uploaded_file = st.file_uploader(
        "Tải lên ảnh bất kỳ (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã tải lên", use_container_width=True)

        user_prompt = st.text_input(
            "Câu hỏi hoặc yêu cầu thêm (Tùy chọn):",
            placeholder="Ví dụ: Giải bài toán này giúp tôi? Hoặc: Địa điểm này ở đâu?"
        )

        if st.button("🚀 Bắt đầu phân tích"):
            if not gemini_api_key:
                st.error("Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets!")
            else:
                try:
                    with st.spinner("AI đang quan sát và phân tích bức ảnh..."):
                        client = genai.Client(api_key=gemini_api_key.strip())

                        default_prompt = (
                            "Hãy quan sát kỹ bức ảnh này và phân tích chi tiết bằng Tiếng Việt theo cấu trúc sau:\n\n"
                            "1. **Phân loại & Tổng quan:** Xác định thể loại bức ảnh (Ví dụ: Bài tập/Toán học, Phong cảnh/Bầu trời, Con người, Đồ vật/Thiết bị, Văn bản/Giấy tờ, Nghệ thuật...).\n"
                            "2. **Phân tích chi tiết theo thể loại:**\n"
                            "   - Nếu là **Bài tập/Toán học/Hình vẽ**: Đọc các dữ kiện, công thức, góc, hình vẽ và đưa ra lời giải hoặc hướng giải.\n"
                            "   - Nếu là **Phong cảnh/Bầu trời/Môi trường**: Phân tích thời tiết, ánh sáng, địa điểm, các yếu tố tự nhiên.\n"
                            "   - Nếu là **Con người**: Mô tả số lượng, hành động, cảm xúc, biểu cảm, trang phục, ngữ cảnh.\n"
                            "   - Nếu là **Đồ vật/Công nghệ**: Nhận diện tên đồ vật, tình trạng, công dụng và đặc điểm nổi bật.\n"
                            "   - Nếu chứa **Văn bản/Chữ viết**: Trích xuất nội dung chữ trong ảnh.\n"
                            "3. **Tóm tắt & Nhận xét:** Kết luận ngắn gọn về ý nghĩa hoặc thông điệp của bức ảnh."
                        )

                        prompt_to_use = user_prompt if user_prompt.strip() else default_prompt

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[image, prompt_to_use]
                        )

                        st.success("Phân tích hoàn tất!")
                        st.markdown("### 📊 Kết quả từ AI:")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Lỗi phân tích hình ảnh: {e}")

# =========================================================
# TÍNH NĂNG 2: BÓC BẰNG ÂM THANH & VIDEO BẰNG GEMINI AI
# =========================================================
elif option == "2. Bóc Băng & Phân Tích Âm Thanh/Video (Audio AI)":
    st.header("🎙️ Bóc Băng & Phân Tích Audio / Video (Gemini AI)")
    st.write("Sử dụng Gemini AI để bóc băng toàn bộ file âm thanh, video chính xác 100% kèm tóm tắt nội dung.")

    uploaded_file = st.file_uploader(
        "Tải lên file Audio hoặc Video (MP3, WAV, MP4, M4A, AAC...)",
        type=["mp3", "mp4", "wav", "m4a", "aac", "flac", "ogg", "mov", "webm"],
    )

    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()

        if ext in ["mp3", "wav", "m4a", "aac", "flac", "ogg"]:
            st.audio(uploaded_file)
        else:
            st.video(uploaded_file)

        audio_prompt = st.text_input(
            "Yêu cầu riêng cho AI (Tùy chọn):",
            placeholder="Ví dụ: Dịch sang Tiếng Việt? Hoặc: Tóm tắt 3 ý chính?"
        )

        if st.button("🚀 Bắt đầu bóc băng toàn bộ"):
            if not gemini_api_key:
                st.error("Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets!")
            else:
                try:
                    with st.spinner("AI đang lắng nghe và trích xuất toàn bộ file âm thanh..."):
                        client = genai.Client(api_key=gemini_api_key.strip())

                        # Lưu tạm file để gửi cho Gemini Client
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name

                        # Upload file lên Gemini
                        audio_file = client.files.upload(file=tmp_path)

                        default_audio_prompt = (
                            "Hãy lắng nghe kỹ toàn bộ file âm thanh/video này và thực hiện các bước sau:\n\n"
                            "1. **Bóc băng nguyên văn (Transcript):** Trích xuất đầy đủ 100% lời nói trong file theo ngữ cảnh ngôn ngữ gốc (không bỏ sót đoạn nào).\n"
                            "2. **Dịch thuật (Nếu là Tiếng Anh/ngôn ngữ khác):** Dịch toàn bộ bản bóc băng sang Tiếng Việt chuẩn nghĩa.\n"
                            "3. **Tóm tắt nội dung chính:** Đưa ra 3-5 ý chính quan trọng nhất mà âm thanh đề cập đến."
                        )

                        prompt_to_use = audio_prompt if audio_prompt.strip() else default_audio_prompt

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[audio_file, prompt_to_use]
                        )

                        st.success("Xử lý hoàn tất!")
                        st.markdown("### 📝 Kết quả bóc băng & Phân tích:")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Lỗi xử lý file âm thanh: {e}")
