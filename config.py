import os
import socket
import requests
from dotenv import load_dotenv

def get_public_ip():
    response = requests.get('https://checkip.amazonaws.com')
    public_ip = response.text.strip()
    return public_ip

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        private_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        hostname = socket.gethostname()
        private_ip = socket.gethostbyname(hostname)
    return private_ip


path = os.getcwd()  # 상위 폴더에서 실행된 경우 -> secret_key.yaml이 상위 폴더에 있음
# path = os.path.dirname(os.path.abspath(__file__)) # 현재 폴더에서 실행된 경우 -> secret_key.yaml이 현재 폴더에 있음

load_dotenv(override=True)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

INSIDE_IP = get_private_ip()
OUTSIDE_IP = get_public_ip()

PORT = 8001
STREAMLIT_PORT = 8501

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

DATA_DIR = os.path.join(path, "data")
IMG_PATH = os.path.join(path, "data", "images")
CSS_PATH = os.path.join(path, "front", "css")
