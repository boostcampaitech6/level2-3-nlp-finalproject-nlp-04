'''
FAISS INDEX TAG 생성 시키는 코드 : 900개의 기술면접 질문 데이터셋을 임베딩 시키는 코드입니다
- 모델 학습과 같은 역할로, inference시에는 사용되지 않습니다
'''

import faiss
import pandas as pd
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader
import os

# 질문 csv 불러오기
data = pd.read_csv('hellojobits_tag.csv')
data = data.iloc[:,0].tolist()

model_name = "sentence-transformers/distiluse-base-multilingual-cased-v2"
model_kwargs = {'device': 'cuda'}
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
model_norm = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

store = FAISS.from_texts(data,model_norm)
store_name="FAISS_INDEX_TAG"
store.save_local(store_name)
print(f"Success to save FAISS index from ./{store_name}")

embeddings = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/distiluse-base-multilingual-cased-v2",
        model_kwargs = {'device': 'cuda'}
    )

new_db = FAISS.load_local(store_name, embeddings, allow_dangerous_deserialization=True)
