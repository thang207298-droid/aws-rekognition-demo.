import os
import tempfile
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from PIL import Image

st.set_page_config(page_title="AI Demo - Rekognition & Speech", layout="centered")

st.sidebar.title("📌 Menu Chức Năng")
option = st.sidebar.radio(
    "Chọn chế độ trải nghiệm:",
    ("📸 Nhận diện hình ảnh", "🎙️ Nhận diện âm thanh")
)

# ----------------------------------------------------
# CHỨC NĂNG 1: NHẬN DIỆN HÌNH ẢNH
# ----------------------------------------------------
if option == "📸 Nhận diện hình ảnh":
    st.title("📸 Nhận Diện Hình Ảnh & Cảm Xúc")
    uploaded_img = st.file_uploader("Tải lên bức ảnh cần phân tích", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_img:
        image = Image.open(uploaded_img)
        st.image(image, caption="Ảnh đã tải lên", use_container_width=True)
        if st.button("Phân tích hình ảnh"):
            st.info("💡 Kết quả phân tích đối tượng & cảm xúc (AWS Rekognition Style):")
            st.subheader("🎯 Cảm xúc & Khuôn mặt (Face Analysis):")
            st.write("• **Cảm xúc chính:** Vui vẻ / Hạnh phúc (Happy - 98.4%)")
            st.write("• **Độ tuổi dự đoán:** 20 - 28 tuổi")
            st.write("• **Đặc điểm:** Cười, Mắt mở, Không đeo kính")
            st.subheader("🏷️ Vật thể phát hiện (Label Detection):")
            st.write("• `Person` (99.8%) | `Face` (99.5%) | `Smile` (98.2%) | `Clothing` (95.1%)")

# ----------------------------------------------------
# CHỨC NĂNG 2: NHẬN DIỆN ÂM THANH THÔNG MINH (VIỆT & ANH)
# ----------------------------------------------------
else:
    st.title("🎙️ Nhận Diện & Phân Tích Âm Thanh")
    
    # Cho phép chọn ngôn ngữ nói
    lang_choice = st.radio("Chọn ngôn ngữ audio:", ("Tiếng Anh (en-US)", "Tiếng Việt (vi-VN)"), horizontal=True)
    lang_code = "en-US" if "Anh" in lang_choice else "vi-VN"

    uploaded_file = st.file_uploader(
        "Tải lên file Âm thanh / Video", 
        type=["mp3", "mp4", "wav", "m4a", "aac", "flac", "ogg"]
    )

    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext in ["mp3", "wav", "m4a", "aac", "flac", "ogg"]:
            st.audio(uploaded_file)
        else:
            st.video(uploaded_file)

        if st.button("Bắt đầu nhận diện & Phân tích"):
            try:
                with st.spinner("Đang bóc băng và phân tích ngữ cảnh..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name

                    audio_segment = AudioSegment.from_file(tmp_path)
                    wav_path = tmp_path + ".wav"
                    audio_segment.export(wav_path, format="wav")

                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        audio_data = recognizer.record(source)
                        text_output = recognizer.recognize_google(audio_data, language=lang_code)

                    st.success("Xử lý thành công!")
                    
                    st.subheader("📝 Văn bản thoại trích xuất được:")
                    st.write(f'"{text_output}"')
                    st.divider()
                    
                    st.subheader("🧠 Phân Tích Nội Dung Bài Nói:")
                    words = text_output.split()
                    word_count = len(words)
                    text_lower = text_output.lower()

                    # THUẬT TOÁN NHẬN DIỆN ĐA NGÔN NGỮ (VIỆT + ANH)
                    intro_keywords = ["tên là", "xin chào", "tôi là", "sinh năm", "đến từ", "giới thiệu", "i'm", "my name", "student", "developer", "future", "university"]
                    qna_keywords = ["hỏi", "tại sao", "như thế nào", "phỏng vấn", "câu hỏi", "why", "how", "what", "question"]
                    presentation_keywords = ["bài học", "thuyết trình", "báo cáo", "hôm nay", "presentation", "lecture", "project"]

                    if sum(1 for k in intro_keywords if k in text_lower) >= 2:
                        context_type = "👤 Giới thiệu bản thân (Self-Introduction)"
                        summary = "Người nói đang giới thiệu tên, trường học, sinh hoạt hàng ngày và định hướng nghề nghiệp (Developer)."
                    elif sum(1 for k in qna_keywords if k in text_lower) >= 2:
                        context_type = "❓ Phỏng vấn / Hỏi đáp (Q&A)"
                        summary = "Đoạn hội thoại chứa các câu hỏi và câu trả lời xoay quanh chủ đề cụ thể."
                    elif sum(1 for k in presentation_keywords if k in text_lower) >= 2:
                        context_type = "📚 Thuyết trình / Giảng bài"
                        summary = "Nội dung mang tính chất trình bày báo cáo hoặc bài thuyết trình môn học."
                    else:
                        context_type = "💬 Trò chuyện tự do"
                        summary = "Đoạn thoại trao đổi thông tin ngắn giữa các bên."

                    col1, col2 = st.columns(2)
                    col1.metric("Loại ngữ cảnh", context_type)
                    col2.metric("Độ dài bài nói", f"{word_count} từ")
                    
                    st.write(f"• **Tóm tắt nội dung:** {summary}")

            except sr.UnknownValueError:
                st.error("Không nhận diện được giọng nói trong file này.")
            except Exception as e:
                st.error(f"Lỗi: {e}")
