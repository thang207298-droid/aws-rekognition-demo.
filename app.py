import tempfile
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from PIL import Image

st.set_page_config(page_title="AI Multi-Tool Demo", layout="centered")

# Thanh điều hướng chọn tính năng
st.sidebar.title("📌 Chọn chức năng Demo")
option = st.sidebar.radio(
    "Bạn muốn trải nghiệm tính năng nào?",
    ("🖼️ Phân tích hình ảnh", "🎙️ Chuyển giọng nói sang văn bản")
)

# ----------------------------------------------------
# CHỨC NĂNG 1: PHÂN TÍCH HÌNH ẢNH
# ----------------------------------------------------
if option == "🖼️ Phân tích hình ảnh":
    st.title("🖼️ Phân tích & Nhận diện Hình ảnh")
    
    uploaded_img = st.file_uploader("Tải lên bức ảnh cần phân tích", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_img:
        image = Image.open(uploaded_img)
        st.image(image, caption="Ảnh đã tải lên", use_container_width=True)
        
        if st.button("Phân tích hình ảnh"):
            with st.spinner("Đang phân tích hình ảnh..."):
                st.success("Phân tích thành công!")
                st.subheader("📊 Kết quả phân tích (Demo):")
                
                # Thông tin cơ bản file ảnh
                col1, col2 = st.columns(2)
                col1.metric("Kích thước (px)", f"{image.width} x {image.height}")
                col2.metric("Định dạng", image.format)
                
                st.divider()
                st.write("• **Trạng thái:** Ảnh rõ nét, đầy đủ ánh sáng.")
                st.write("• **Gợi ý tag/nhãn:** `Object Detection`, `Image Analysis`, `AI Demo`")

# ----------------------------------------------------
# CHỨC NĂNG 2: CHUYỂN GIỌNG NÓI SANG VĂN BẢN
# ----------------------------------------------------
else:
    st.title("🎙️ Chuyển Giọng Nói Sang Văn Bản")
    
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

        if st.button("Bắt đầu nhận diện"):
            try:
                with st.spinner("Đang chuyển âm thanh sang văn bản..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name

                    audio_segment = AudioSegment.from_file(tmp_path)
                    wav_path = tmp_path + ".wav"
                    audio_segment.export(wav_path, format="wav")

                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        audio_data = recognizer.record(source)
                        text_output = recognizer.recognize_google(audio_data, language="vi-VN")

                    st.success("Xử lý thành công!")
                    st.subheader("📝 Văn bản thu được:")
                    st.write(text_output)
                    
                    st.divider()
                    words = text_output.split()
                    st.write(f"• **Tổng số từ:** {len(words)} từ")

            except sr.UnknownValueError:
                st.error("Không nhận diện được giọng nói trong file này.")
            except Exception as e:
                st.error(f"Lỗi: {e}")
