import base64
import json
import os
import sys
from time import time

import jwt
import requests
import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config import CLIENT_ID


# OIDC를 위해 공개키 가져오기
def get_public_key(kid):
    jwks_uri = "https://kauth.kakao.com/.well-known/jwks.json"  # OIDC 공개키 목록을 가져올 수 있는 엔드포인트

    # 공개키 목록 가져오기
    response = requests.get(jwks_uri)
    if response.status_code != 200:
        raise Exception("Failed to fetch public keys")

    jwks = response.json()

    # 특정 kid에 해당하는 공개키 찾기
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    raise Exception("Public key not found for kid: {}".format(kid))


def verify_token(token):
    """
    주어진 토큰을 검증하는 함수입니다.

    Parameters:
        token (str): 검증할 토큰 문자열

    Returns:
        tuple: 검증 결과와 디코딩된 페이로드
            - 첫 번째 요소는 검증 결과를 나타내는 불리언 값입니다.
              True는 토큰이 유효하고 검증에 성공했음을 나타내며, False는 토큰이 유효하지 않거나 검증에 실패했음을 나타냅니다.
            - 두 번째 요소는 디코딩된 페이로드입니다.
              검증에 성공한 경우에만 반환되며, 딕셔너리 형태로 토큰에 포함된 정보를 담고 있습니다.
              검증에 실패한 경우에는 해당 실패 원인을 나타내는 문자열이 반환됩니다.
    """
    # 토큰 분리
    if token == None:
        return False, "Token is None"

    header, payload, signature = token.split(".")

    # 패딩 추가(페이로드 디코딩)
    padding_length = len(payload) % 4
    payload += "=" * padding_length
    decoded_payload = base64.b64decode(payload)

    # 디코딩된 payload를 JSON 형식의 문자열에서 딕셔너리로 변환
    decoded_payload = json.loads(decoded_payload)

    # 필요한 정보 추출
    issuer = decoded_payload["iss"]         # 발급자
    audience = decoded_payload["aud"]       # 대상자
    expiration_time = decoded_payload["exp"]# 만료 시간
    current_time = int(time())

    # 토큰 유효성 검사
    if issuer != "https://kauth.kakao.com": # JWT 발급자 체크
        return False, "Issuer mismatch"
    if audience != CLIENT_ID:            # JWT 대상자 체크
        return False, "Audience mismatch"   
    if expiration_time < current_time:      # JWT 만료 시간 체크
        return False, "Token expired"

    # 헤더 디코딩 및 kid 값 추출
    decoded_header = base64.b64decode(header + "=" * (-len(header) % 4))
    decoded_header = json.loads(decoded_header)
    kid = decoded_header["kid"]

    # 공개키 목록 조회
    public_key = get_public_key(kid)

    # 서명 검증
    # Decode the public key data
    modulus_bytes = base64.urlsafe_b64decode(public_key["n"] + "==")
    exponent_bytes = base64.urlsafe_b64decode(public_key["e"] + "==")

    # Convert bytes to integers
    modulus = int.from_bytes(modulus_bytes, "big")
    exponent = int.from_bytes(exponent_bytes, "big")

    # Construct RSA public key
    rsa_public_numbers = rsa.RSAPublicNumbers(exponent, modulus)
    public_key = rsa_public_numbers.public_key()

    # Serialize public key to PEM format
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Use RSA public key to decode and verify the JWT token
    try:
        decoded_payload = jwt.decode(token, public_key_pem, algorithms=["RS256"], options={"verify_aud": False})
        return True, decoded_payload
    except jwt.ExpiredSignatureError:
        return False, "Expired token"
    except jwt.InvalidSignatureError:
        return False, "Invalid signature"


def check_login(id_token: str):
    """
    ID 토큰을 검증하여 로그인 여부를 확인합니다.

    Returns:
        bool: 로그인 여부를 나타내는 불리언 값입니다.

    Raises:
        HTTPException: 로그인이 안 된 경우, 카카오 페이지로 리다이렉트합니다.
    """

    res, message = verify_token(id_token)

    return res, message


# 토큰 검증
if __name__ == "__main__":
    # 토큰 발급(세션 테스트용)
    id_token = "id_token"
    """
    Header: algorithm, token type
    {
      "kid": "9f252dadd5f233f93d2fa528d12fea",  # 공개키 식별자
      "typ": "JWT",                             # 토큰 타입
      "alg": "RS256"                            # 암호화 알고리즘
    }

    Payload: data
    {         
      "aud": "0123456789zbcdefghijklmnopqrstuv", # 대상자, REST_API_KEY
      "sub": "0123456789",              # 사용자 ID
      "auth_time": 2147483647,          # 인증 시간, UNIX timestamp 
      "iss": "https://kauth.kakao.com", # 발급자, 카카오
      "nickname": "죽전동 불주먹",       # 카카오톡에서 사용자 이름
      "exp": 2147483647,                # 만료 시간, UNIX timestamp
      "iat": 2147483647,                # 발급 시간, UNIX timestamp
      "email": "kooqoo@kakao.com"
    }

    """


    is_valid, message = verify_token(id_token)
    if is_valid:
        print("토큰이 유효합니다.", message)
    else:
        print("토큰이 유효하지 않습니다:", message)
