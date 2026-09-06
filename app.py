import tempfile
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment

st.set_page_config(page_title="AI Speech to Text", layout="centered")
st.title("🎙️ Bóc Băng Âm Thanh / Video")

uploaded_file = st.file_uploader(
    "Tải lên file Audio hoặc Video", 
    type=["mp3", "mp4", "wav", "m4a", "aac", "flac", "ogg", "mov", "avi", "mkv", "webm"]
)

if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()
    
    if ext in ["mp3", "wav", "m4a", "aac", "flac", "ogg"]:
        st.audio(uploaded_file)
    else:
        st.video(uploaded_file)

    if st.button("Bắt đầu bóc băng"):
        try:
            with st.spinner("Đang chuyển đổi định dạng và bóc băng âm thanh..."):
                # Lưu file tạm
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                # Convert audio sang WAV chuẩn PCM
                audio_segment = AudioSegment.from_file(tmp_path)
                wav_path = tmp_path + ".wav"
                audio_segment.export(wav_path, format="wav")

                # Bóc băng giọng nói
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)
                    # Chọn language="vi-VN" cho tiếng Việt hoặc "en-US" cho tiếng Anh
                    text_output = recognizer.recognize_google(audio_data, language="vi-VN")

                st.success("Xử lý hoàn tất!")
                st.subheader("📝 Văn bản trích xuất:")
                if text_output:
                    st.write(text_output)
                    st.divider()
                    word_count = len(text_output.split())
                    st.write(f"• **Tổng số từ:** {word_count} từ")
                else:
                    st.write("Không nhận diện được nội dung thoại trong file.")

        except sr.UnknownValueError:
            st.error("Không thể nhận diện âm thanh trong file. Hãy kiểm tra lại độ rõ của giọng nói.")
        except Exception as e:
            st.error(f"Lỗi xử lý: {e}")
