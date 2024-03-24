import faiss
import pandas as pd
import numpy as np
from langchain.vectorstores import FAISS
import os
from sentence_transformers import SentenceTransformer, util
import time

# 질문 csv 불러오기
data = pd.read_csv('hellojobits_dataset_final.csv')
data = data.iloc[:,1].tolist()

model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')

query = ['프로젝트명: Upbit API 투자 자동화 서비스 프로젝트 내용 및 사용기술: 주식매매에 쓰는 시간을 절약하기 위해 원하는 매매기법을 적용한 투자 자동화 서비스를 개발하였습니다. Upbit API를 활용하여 기능을 개발하고 구현하였으며, 유지보수와 배포를 담당하였습니다. 관련 기술로는 pyupbit API와 FastAPI를 사용하였습니다.']
p_embs = model.encode(data)
q_embs = model.encode(query)
niter=5
emb_dim = p_embs.shape[-1]
k = 10
n_cluster = 24 ## 4*sqrt(900)

# 1. Clustering
index_flat = faiss.IndexFlatL2(emb_dim)
clus = faiss.Clustering(emb_dim, n_cluster)
clus.verbose = True
clus.niter = niter
clus.train(p_embs, index_flat)
centroids = faiss.vector_float_to_array(clus.centroids)
centroids = centroids.reshape(n_cluster, emb_dim)

quantizer = faiss.IndexFlatL2(emb_dim)
quantizer.add(centroids)

# 2. SQ8 + IVF indexer (IndexIVFScalarQuantizer)
indexer = faiss.IndexIVFScalarQuantizer(quantizer, quantizer.d, quantizer.ntotal, faiss.METRIC_L2)
indexer.train(p_embs)
indexer.add(p_embs)

# 3. Search using indexer
start_time = time.time()
D, I = indexer.search(q_embs, k)
print("--- %s seconds ---" % (time.time() - start_time))


for i, q in enumerate(query):
  print("[Search query]\n", q, "\n")

  d = D[i]
  i = I[i]
  for j in range(k):
    print("Top-%d passage with distance %.4f" % (j+1, d[j]))
    print(data[i[j]])
  print('\n')