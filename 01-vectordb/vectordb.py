import os
import chromadb
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction,SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer


#openai key 설정
os.environ['OPENAI_API_KEY'] = 'openai-key'
api_key = os.environ.get('OPENAI_API_KEY')

# chromadb 이용해 질문 임베딩 저장
client = chromadb.Client()
sentence_transformer_ef = SentenceTransformerEmbeddingFunction(model_name="jhgan/ko-sbert-nli")
vector_collection = client.get_or_create_collection(name = 'jobits', embedding_function = sentence_transformer_ef,metadata = {"hnsw:space": "cosine"})

documents = pd.read_csv('hello_jobits_question_AI.csv')['Text'].to_list()
document_ids = list(map(lambda tup: f"id{tup[0]}", enumerate(documents)))
vector_collection.add(documents=documents, ids=document_ids)


# query 결과 살피기
text = '''핵심 업무 및 역량 요구사항:
Text Detection / Text Recognition을 위한 OCR 모델 개발 및 성능 최적화에 중점을 둡니다.
필요한 역량은 OCR 현업 서비스 경험, SOTA OCR 모델 Trend 및 Research 역량, Quantization 및 Edge Device 서비스 경험, Vision 및 Neural Network 구조에 대한 높은 이해도입니다.
토스에서의 업무에 대한 강조점:
비즈니스에 임팩트를 내는 역할을 강조하며, 주어진 데이터 이외의 집계되지 않는 데이터를 모델에 녹여내는 데 중점을 두고 있습니다.
금융 관련 데이터뿐만 아니라 유저에 대한 이해를 바탕으로 슈퍼앱을 운영하여 기여할 수 있는 역량이 중요합니다.'''

results = vector_collection.query(query_texts = text, n_results = 10)
