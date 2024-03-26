import os
import sys
import re
import cohere
import faiss
import pandas as pd
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config import COHERE_API_KEY  # COHERE_API_KEY 불러오기

def faiss_inference(query):
    '''
    faiss를 이용해 JD 키워드 한줄한줄 받아와서 유사한 기술면접 질문 4개씩을 불러옵니다.
    output으로는 (4 * 키워드 줄 개수 - 중복된 문장)개의 질문이 반환됩니다
    '''
    embeddings = HuggingFaceEmbeddings(
            model_name = "sentence-transformers/distiluse-base-multilingual-cased-v2",
            model_kwargs = {'device': 'cuda'}
        )
    store_name="./FAISS_INDEX_TAG"
    new_db = FAISS.load_local(store_name, embeddings, allow_dangerous_deserialization=True)
    results = query.split('\n')
    final_result = []
    for i in results:
        docs = new_db.similarity_search(i, k=4)
        page_contents = [final_result.append(doc.page_content) for doc in docs]
    # 중복된 문장 제거    
    final_result = list(set(final_result))
    
    return final_result
    

# reranking 함수
def reranker(query, final_result):
    '''
    앞선 faiss retriver에서 한번 걸러진 질문들로 reranking합니다.
    query로는 기존 JD 전체가 들어갑니다.
    output : 3개의 질문 
    '''
    co = cohere.Client(COHERE_API_KEY)
    results = co.rerank(query=query, documents=final_result, top_n=3, model="rerank-multilingual-v2.0")
    results = results.results
    questions = []
    for idx, r in enumerate(results):
        doc_str = final_result[r.index]
        cleaned_doc = re.sub(r'@.*?@ ', '', doc_str) # tagging 된 값들 제거
        questions.append(cleaned_doc)
    return questions
