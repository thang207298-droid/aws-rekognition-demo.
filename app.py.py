import streamlit as st
import boto3
from PIL import Image
import io

st.set_page_config(page_title="AWS Rekognition Demo", layout="centered")
st.title("AI Nhận Diện Khuôn Mặt - AWS Rekognition")

# Nhập Access Key từ file rootkey.csv của bạn
st.sidebar.header("Cấu hình AWS")
aws_access_key = st.sidebar.text_input("AWS Access Key ID", type="password")
aws_secret_key = st.sidebar.text_input("AWS Secret Access Key", type="password")
region = "ap-southeast-2"  # Vùng Sydney của tài khoản bạn

uploaded_file = st.file_uploader("Chọn ảnh để phân tích", type=["jpg", "jpeg", "png"])

if uploaded_file and aws_access_key and aws_secret_key:
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh đã chọn", use_container_width=True)
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
    img_bytes = img_byte_arr.getvalue()

    if st.button("Phân tích ngay"):
        try:
            client = boto3.client(
                'rekognition',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            
            response = client.detect_faces(Image={'Bytes': img_bytes}, Attributes=['ALL'])
            faces = response['FaceDetails']
            st.success(f"Phát hiện {len(faces)} khuôn mặt!")
            
            for idx, face in enumerate(faces):
                st.subheader(f"Khuôn mặt #{idx+1}")
                st.write(f"• **Tuổi dự đoán:** {face['AgeRange']['Low']} - {face['AgeRange']['High']}")
                st.write(f"• **Cảm xúc chính:** {face['Emotions'][0]['Type']} ({face['Emotions'][0]['Confidence']:.1f}%)")
                st.write(f"• **Đeo kính:** {'Có' if face['Eyeglasses']['Value'] else 'Không'}")
                st.write(f"• **Mỉm cười:** {'Có' if face['Smile']['Value'] else 'Không'}")
                
        except Exception as e:
            st.error(f"Lỗi: {e}")