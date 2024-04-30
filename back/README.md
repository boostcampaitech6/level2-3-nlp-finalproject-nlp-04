# 목차
1. Docker 설치하기
> 1. Docker 설치 여부 확인
> 2. Docker 설치하기
3. Docker로 MongoDB 실행하기
> 1. 컨테이너 만들기
> 2. 환경변수 설정하기
> 3. MongoDB Compass로 데이터 베이스 보기
>> 1. MoongoDB Compass 설치하기
>> 2. 연결하기
3. [백엔드] FastAPI 서버 실행 하기
4. [프론트엔드] Streamlit 앱 실행하기

# 1. Docker 설치하기
## 1-1. Docker 설치 여부 확인
```
docker -V
```
해당 명령어를 입력 후 설치가 되어있다는 것을 확인하면 `2. Docker로 MongoDB 실행하기`로 넘어가시면 됩니다.
## 1-2. Docker 설치하기
```
# 1. 우분투 시스템 패키지 업데이트
sudo apt-get update

# 2. 필요한 패키지 설치
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common

# 3. Docker의 공식 GPG키를 추가
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
 
# 4. Docker의 공식 apt 저장소를 추가
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
 
# 5. 시스템 패키지 업데이트
sudo apt-get update

# 6. Docker 설치
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
 
# 7. Docker가 설치 확인
# 7-1. 도커 실행상태 확인
sudo systemctl status docker
```

# 2. Docker로 MongoDB 실행하기
## 2-1. 컨테이너 만들기
```
docker pull mongo

docker run --name [컨테이너이름] -d \
-e MONGO_INITDB_ROOT_USERNAME=admin \
-e MONGO_INITDB_ROOT_PASSWORD=[비밀번호] \
-v [로컬의 데이터 저장소]:[컨테이너 내의 데이터 저장소] \
-p 127.0.0.1:27017:27017 mongo

docker ps -a # 이거로 실행 여부 확인

# 만약 컨테이너 내부의 Mongo Shell에 접속하고 싶으면 아래의 명령어를 통해 접속이 가능합니다.
# docker exec -it [컨테이너이름] mongosh -u admin -p
```

## 2-2. 환경변수 설정하기
- `MONGO_PASSWORD`에 본인의 비밀번호를 설정하여 사용하시면 됩니다.
- `mongodb.py` 코드 내에서 수정이 가능하나 커밋할 때 Staged 상태인지 확인 후 커밋을 부탁드립니다.

# 3. MongoDB Compass로 데이터 베이스 보기
> 해당 부분은 `mongosh`이 아닌 GUI로 DB에 접근할 때 사용합니다.
> 코드 실행의 필수적인 부분은 아닙니다.
## 3-1. MongoDB Compass 설치하기
https://www.mongodb.com/try/download/compass
<- 링크에서 Download를 통해 설치를 합니다.
- Apple Silicon이 탑재된 Mac 컴퓨터를 사용하는 사용자의 경우 arm64 버전을 다운로드 받는 것을 추천합니다.

## 3-2. MongoDB Compass 연결하기
1. 새로운 연결 시에 `Advanced Connection Options` 토글을 열어줍니다.
2. `Athentication` 탭에서 도커 컨테이너를 만들었을 때 설정한 Username과 Password를 입력합니다.
3. `TLS/SSL` 탭에서 `SSL/TLS Connection` 옵션을 Off합니다.
4. `Proxy/SSH` 탭으로 이동합니다.
> 1. `SSH Tunnel/Proxy Method`에서 `SSH with Password`를 선택합니다.
> 2. `SSH Hostname`에 접속할 IP 주소를 입력합니다.
> 3. 기타 아래에 본인 환경에 맞게 설정하고 연결합니다.

