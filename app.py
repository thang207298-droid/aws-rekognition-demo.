import io
import boto3
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="AWS Rekognition Multi-Purpose AI", layout="centered"
)
st.title("AI Phân Tích & Nhận Diện Hình Ảnh Đa Năng - AWS Rekognition")

st.sidebar.header("Cấu hình AWS")
aws_access_key = st.sidebar.text_input("AWS Access Key ID", type="password")
aws_secret_key = st.sidebar.text_input("AWS Secret Access Key", type="password")
region = "ap-southeast-2"

uploaded_file = st.file_uploader(
    "Chọn ảnh để phân tích", type=["jpg", "jpeg", "png"]
)

if uploaded_file and aws_access_key and aws_secret_key:
  image = Image.open(uploaded_file)
  st.image(image, caption="Ảnh đã chọn", use_container_width=True)

  img_byte_arr = io.BytesIO()
  image.save(
      img_byte_arr, format=image.format if image.format else "JPEG"
  )
  img_bytes = img_byte_arr.getvalue()

  if st.button("Phân tích ngay"):
    try:
      client = boto3.client(
          "rekognition",
          aws_access_key_id=aws_access_key,
          aws_secret_access_key=aws_secret_key,
          region_name=region,
      )

      # 1. Nhận diện Vật thể, Cảnh quan & Nhãn (Detect Labels)
      response_labels = client.detect_labels(
          Image={"Bytes": img_bytes}, MaxLabels=10, MinConfidence=70
      )
      labels = response_labels["Labels"]

      st.subheader("📌 Nhãn & Vật thể phát hiện được:")
      for label in labels:
        st.write(f"• **{label['Name']}**: {label['Confidence']:.1f}%")

      # 2. Nhận diện Khuôn mặt (Detect Faces - nếu trong ảnh có người)
      response_faces = client.detect_faces(
          Image={"Bytes": img_bytes}, Attributes=["ALL"]
      )
      faces = response_faces["FaceDetails"]

      if faces:
        st.divider()
        st.subheader(f"👤 Chi tiết khuôn mặt ({len(faces)} người):")
        for idx, face in enumerate(faces):
          st.write(
              f"**Người #{idx+1}:** {face['AgeRange']['Low']}-{face['AgeRange']['High']} tuổi | "
              f"Cảm xúc: {face['Emotions'][0]['Type']} ({face['Emotions'][0]['Confidence']:.1f}%)"
          )

    except Exception as e:
      st.error(f"Lỗi: {e}")
