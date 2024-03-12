import streamlit as st
import requests
import json

st.title('Hello JobITS')

st.image('https://cdn-icons-png.flaticon.com/512/6134/6134346.png', width=200)  # Replace with your robot emoticon URL

# 로그인 세션 관리를 위한 세션 상태 설정
if 'auth_token' not in st.session_state:
    st.session_state['auth_token'] = None

# 로그인 폼
def login_form():
    with st.form(key='login_form'):
        username = st.text_input(label='Username')
        password = st.text_input(label='Password', type='password')
        submit_button = st.form_submit_button(label='Login')

        if submit_button:
            # FastAPI 백엔드로 로그인 요청 보내기
            response = requests.post(
                'http://127.0.0.1:8000/token',
                data={
                    'username': username,
                    'password': password
                }
            )
            if response.status_code == 200:
                auth_token = response.json().get('access_token')
                st.session_state['auth_token'] = auth_token
                st.success('Logged in successfully!')
            else:
                st.error('Login failed!')

# 회원가입 폼
def signup_form():
    with st.form(key='signup_form'):
        new_username = st.text_input(label='New Username')
        new_password = st.text_input(label='New Password', type='password')
        submit_button = st.form_submit_button(label='Sign up')

        if submit_button:
            # FastAPI 백엔드로 회원가입 요청 보내기
            response = requests.post(
                'http://127.0.0.1:8000/signup',
                data={
                    'username': new_username,
                    'password': new_password
                }
            )
            if response.status_code == 200:
                st.success('Signed up successfully!')
            else:
                st.error('Signup failed!')

# 로그인 상태 확인 및 개인 페이지 구성
def personal_page():
    st.write('Welcome to your personal page!')
    file = st.file_uploader('Upload a file')
    if file is not None:
        files = {'file': (file.name, file, 'multipart/form-data')}
        # FastAPI 백엔드로 파일 업로드 요청 보내기
        response = requests.post(
            'http://127.0.0.1:8000/uploadfile/',
            headers={'Authorization': f'Bearer {st.session_state["auth_token"]}'},
            files=files
        )
        if response.status_code == 200:
            st.success('File uploaded successfully!')
        else:
            st.error('File upload failed!')

# 메인 앱 로직
if st.session_state['auth_token']:
    personal_page()
else:
    if st.button('Login'):
        login_form()
    if st.button('Sign up'):
        signup_form()