import logging
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader

#openai key 설정
os.environ['OPENAI_API_KEY'] = 'openai-key'
api_key = os.environ.get('OPENAI_API_KEY')

# 질문 csv 불러오기
loader = CSVLoader(file_path = 'hello_jobits_question_AI.csv')
data = loader.load()

# 객체 생성
llm = ChatOpenAI()
embedding = OpenAIEmbeddings()
vectordb = Chroma.from_documents(documents = data, embedding = embedding)

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

# multiquery 이용해 retrieval 진행
query = '''핵심 업무 및 역량 요구사항:
Text Detection / Text Recognition을 위한 OCR 모델 개발 및 성능 최적화에 중점을 둡니다.
필요한 역량은 OCR 현업 서비스 경험, SOTA OCR 모델 Trend 및 Research 역량, Quantization 및 Edge Device 서비스 경험, Vision 및 Neural Network 구조에 대한 높은 이해도입니다.
토스에서의 업무에 대한 강조점:
비즈니스에 임팩트를 내는 역할을 강조하며, 주어진 데이터 이외의 집계되지 않는 데이터를 모델에 녹여내는 데 중점을 두고 있습니다.
금융 관련 데이터뿐만 아니라 유저에 대한 이해를 바탕으로 슈퍼앱을 운영하여 기여할 수 있는 역량이 중요합니다.'''

retriever_from_llm = MultiQueryRetriever.from_llm(retriever=vectordb.as_retriever(), llm=llm)
docs = retriever_from_llm.get_relevant_documents(query=query)
for doc in docs:
    print(doc)