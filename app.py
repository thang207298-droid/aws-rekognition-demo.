import tempfile
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment

st.set_page_config(page_title="Speech to Text Demo", layout="centered")
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

    if st.button("Bắt đầu nhận diện & phân tích"):
        try:
            with st.spinner("Đang xử lý âm thanh..."):
                # Lưu file tạm & convert sang WAV
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                audio_segment = AudioSegment.from_file(tmp_path)
                wav_path = tmp_path + ".wav"
                audio_segment.export(wav_path, format="wav")

                # Nhận diện giọng nói
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)
                    text_output = recognizer.recognize_google(audio_data, language="vi-VN")

                st.success("Xử lý thành công!")
                
                # Hiển thị văn bản
                st.subheader("📝 Văn bản thu được:")
                st.write(text_output)
                
                st.divider()
                
                # Phân tích đơn giản cho bài Demo
                st.subheader("📊 Phân tích nhanh:")
                words = text_output.split()
                col1, col2 = st.columns(2)
                col1.metric("Tổng số từ", f"{len(words)} từ")
                col2.metric("Tổng số ký tự", f"{len(text_output)} ký tự")

        except sr.UnknownValueError:
            st.error("Không nhận diện được giọng nói trong file này.")
        except Exception as e:
            st.error(f"Lỗi: {e}")
