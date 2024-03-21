import os

import yaml

path = os.getcwd()  # 상위 폴더에서 실행된 경우 -> secret_key.yaml이 상위 폴더에 있음
# path = os.path.dirname(os.path.abspath(__file__)) # 현재 폴더에서 실행된 경우 -> secret_key.yaml이 현재 폴더에 있음

with open(os.path.join(path, "secret_key.yaml"), "r") as yaml_file:
    cfg = yaml.safe_load(yaml_file)

OPENAI_API_KEY = cfg["OPENAI_API_KEY"]

INSIDE_IP = cfg["IP"]["INSIDE_IP"]
OUTSIDE_IP = cfg["IP"]["OUTSIDE_IP"]

REST_API_KEY = cfg["Kakaologin"]["REST_API_KEY"]
REDIRECT_URI = f"http://{OUTSIDE_IP}:{cfg['PORT']}/auth"


PORT = cfg["PORT"]
STREAMLIT_PORT = cfg["STREAMLIT"]["PORT"]
DATA_DIR = cfg["STREAMLIT"]["DATA_DIR"]

KEY_FILE = cfg["SSL"]["KEY_FILE"]
CERT_FILE = cfg["SSL"]["CERT_FILE"]
# FRONT_FILE_PATH =

