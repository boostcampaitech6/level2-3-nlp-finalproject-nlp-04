from pymongo import MongoClient

# pymongo 라이브러리를 설치합니다.
# pip install pymongo

# MongoDB 서버에 연결
client = MongoClient('mongodb://localhost:27017/')

# 데이터베이스 선택
db = client['mydatabase']

# 컬렉션 선택
collection = db['mycollection']

# # 데이터 삽입
# post = {"author": "Mike", "text": "My first blog post!", "tags": ["mongodb", "python", "pymongo"]}
# post_id = collection.insert_one(post).inserted_id
# print(f"Inserted post id {post_id}")

# # 데이터 조회
# for post in collection.find({"author": "Mike"}):
#     print(post)

# # 데이터 업데이트
# collection.update_one({'author': 'Mike'}, {'$set': {'text': 'My updated blog post'}})

# # 업데이트된 데이터 확인
# for post in collection.find({"author": "Mike"}):
#     print(post)

# # 데이터 삭제
# # # collection.delete_one({'author': 'Mike'})

# 삭제된 후 데이터 확인
for post in collection.find():
    print(post)

# MongoDB 서버와의 연결 종료
client.close()