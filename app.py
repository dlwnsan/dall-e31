import streamlit as st
import openai
import requests
from PIL import Image
from io import BytesIO
import uuid
import os
import json

# OpenAI API 키 설정
api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key)

# 세션 상태 초기화
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = str(uuid.uuid4())
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'is_generating' not in st.session_state:
    st.session_state['is_generating'] = False

# 이미지 저장 디렉토리 설정
SAVE_DIR = "generated_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        img = Image.open(BytesIO(img_response.content))
        
        # 이미지 저장
        filename = f"{st.session_state['user_id']}_{len(st.session_state['history'])}.png"
        filepath = os.path.join(SAVE_DIR, filename)
        img.save(filepath)
        
        return img, filepath
    except Exception as e:
        st.error(f"이미지 생성 중 오류 발생: {str(e)}")
        return None, None

def main():
    st.title("DALL-E 3 이미지 생성기")
    
    prompt = st.text_area("이미지에 대한 설명을 입력하세요...")
    
    if st.button("이미지 생성", disabled=st.session_state['is_generating']):
        st.session_state['is_generating'] = True
        
        with st.spinner("이미지 생성 중..."):
            img, filepath = generate_image(prompt)
        
        if img:
            st.image(img, caption="생성된 이미지")
            st.success("이미지가 생성되었습니다!")
            
            # 다운로드 버튼
            with open(filepath, "rb") as file:
                btn = st.download_button(
                    label="이미지 다운로드",
                    data=file,
                    file_name=os.path.basename(filepath),
                    mime="image/png"
                )
            
            # 히스토리에 추가
            st.session_state['history'].append({
                "prompt": prompt,
                "image_path": filepath
            })
        
        st.session_state['is_generating'] = False
    
    # 히스토리 표시
    st.subheader("생성 기록")
    for idx, item in enumerate(st.session_state['history']):
        st.text(f"프롬프트: {item['prompt']}")
        st.image(item['image_path'], caption=f"생성된 이미지 {idx+1}")
        st.markdown("---")

if __name__ == "__main__":
    main()
