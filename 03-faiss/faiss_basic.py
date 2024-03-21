import faiss
import pandas as pd
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader
import os

# 질문 csv 불러오기
data = pd.read_csv('hellojobits_dataset_final.csv')
data = data.iloc[:,1].tolist()

model_name = "intfloat/multilingual-e5-large"
model_kwargs = {'device': 'cuda'}
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
model_norm = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

store = FAISS.from_texts(data,model_norm)
store_name="FAISS_INDEX"
store.save_local(store_name)
print(f"Success to save FAISS index from ./{store_name}")

embeddings = HuggingFaceEmbeddings(
        model_name = "intfloat/multilingual-e5-large",
        model_kwargs = {'device': 'cuda'}
    )

new_db = FAISS.load_local(store_name, embeddings)
docs = new_db.similarity_search("프로젝트명: 객체인식 및 열화상 모듈을 통한 고열자 탐지 서비스, 프로젝트 내용 및 사용기술: Covid-19 시기에 열화상카메라의 비용문제를 해결하기 위해 객체인식 및 열화상 모듈을 활용한 고열자 탐지 서비스를 개발하였습니다. yolo학습, 열화상 카메라 API 활용, 센서/스피커 연동 등을 담당하였으며, 관련 기술로는 yolo, mlx90640 API, Raspberry Pi, C/C++, Java 등을 사용하였습니다.", k=5)
print(len(docs))

print(docs)
