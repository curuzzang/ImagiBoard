import streamlit as st
import openai
import requests
from io import BytesIO

st.set_page_config(page_title="나의 그림상자 (Assistant API)", layout="wide")
st.title("🖼️ 나의 그림상자 - AI와 함께 콜라주 만들기")

openai.api_key = st.secrets["api_key"]

left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("🎨 상상력 입력하기")

    with st.form("prompt_form"):
        theme = st.text_input("🎯 주제", placeholder="예: 꿈속을 걷는 느낌")
        genre = st.selectbox("🖌️ 스타일", [
            "수채화", "유화", "카툰", "픽셀 아트", "3D 렌더링", "사이버펑크", 
            "스케치풍", "클림트 스타일", "큐비즘", "사진 같은 리얼리즘", "아르누보", "낙서풍 (Doodle)"
        ])
        elements = st.text_input("🌟 포함할 요소들", placeholder="예: 고양이, 우산, 별, 밤하늘")
        color_tone = st.selectbox("🎨 색상 톤", [
            "따뜻한 파스텔톤", "선명한 원색", "몽환적 퍼플", "차가운 블루", "빈티지 세피아", 
            "형광 네온", "모노톤 (흑백)", "대비 강한 컬러", "브라운 계열", "연보라+회색", 
            "다채로운 무지개", "연한 베이지", "청록+골드"
        ])
        mood = st.multiselect("💫 감정 / 분위기", [
            "몽환적", "고요함", "희망", "슬픔", "그리움", "설렘", "불안정함", "자유로움",
            "기대감", "공허함", "감사함", "외로움", "기쁨", "어두움", "차분함", "위로", "용기", "무한함", "즐거움", "강렬함"
        ], default=["몽환적"])
        viewpoint = st.selectbox("📷 시점 / 구도", [
            "정면", "항공 시점", "클로즈업", "광각", "역광", "뒷모습", "소프트 포커스", "하늘을 올려다보는 시점"
        ])
        submit = st.form_submit_button("✨ 프롬프트 및 이미지 생성")

with right_col:
    if submit:
        with st.spinner("GPT-4o가 상상 중입니다..."):
            try:
                # GPT 프롬프트 생성 지시문
                instruction = f"""
You are an assistant that generates an image prompt and creates an image using DALL·E 3.
User wants to express a theme through visual art. 
Generate a vivid English image prompt based on the user's choices.

Theme: {theme}
Style: {genre}
Elements: {elements}
Color tone: {color_tone}
Mood: {', '.join(mood)}
Viewpoint: {viewpoint}

Return ONLY the image description in English that can be used for DALL·E 3.
"""

                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": instruction}]
                )
                dalle_prompt = response["choices"][0]["message"]["content"].strip()
                st.session_state["dalle_prompt"] = dalle_prompt

                # 이미지 생성
                image_response = openai.Image.create(
                    model="dall-e-2",
                    prompt=dalle_prompt,
                    size="1024x1024",
                    n=1
                )
                image_url = image_response["data"][0]["url"]
                st.session_state["image_url"] = image_url

            except Exception as e:
                st.error(f"에러: {e}")

    # 이미지와 프롬프트가 세션에 저장되어 있다면 표시
    if "image_url" in st.session_state and "dalle_prompt" in st.session_state:
        st.markdown("### 📝 생성된 영어 프롬프트")
        st.code(st.session_state["dalle_prompt"])

        st.image(st.session_state["image_url"], caption="🎉 생성된 이미지", use_column_width=True)

        # ✅ 다운로드 버튼도 조건문 안에 포함
        image_data = requests.get(st.session_state["image_url"]).content
        st.download_button(
            label="📥 이미지 다운로드 (PNG)",
            data=BytesIO(image_data),
            file_name="my_art_box_result.png",
            mime="image/png"
        )

