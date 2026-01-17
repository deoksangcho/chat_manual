"""
벡터 스토어 모듈
- ChromaDB 초기화 및 관리
- BM25 인덱스 생성 및 관리
- 하이브리드 검색 (Vector + BM25)
"""

import os
import pickle
from typing import List, Dict
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from rank_bm25 import BM25Okapi


def create_vectorstore(chunks: List[Document], config: Dict, persist_directory: str = None) -> Chroma:
    """
    ChromaDB 생성 및 저장
    
    Args:
        chunks: 청크된 문서 리스트
        config: config.yaml의 embedding 설정
        persist_directory: 저장 경로 (기본값: config의 chroma_path)
        
    Returns:
        Chroma 벡터스토어
    """
    if persist_directory is None:
        persist_directory = config['database']['chroma_path']
    
    # OpenAI 임베딩 초기화
    embeddings = OpenAIEmbeddings()
    
    # 배치 처리 (한 번에 100개씩)
    batch_size = 100
    vectorstore = None
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"      진행 중: {i + len(batch)}/{len(chunks)} 청크 처리 완료")
        
        if vectorstore is None:
            # 첫 번째 배치로 vectorstore 생성
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=persist_directory
            )
        else:
            # 이후 배치는 추가
            vectorstore.add_documents(batch)
    
    return vectorstore


def load_vectorstore(config: Dict) -> Chroma:
    """
    기존 ChromaDB 로드
    
    Args:
        config: config.yaml 설정
        
    Returns:
        Chroma 벡터스토어
    """
    persist_directory = config['database']['chroma_path']
    
    # OpenAI 임베딩 초기화
    embeddings = OpenAIEmbeddings()
    
    # 기존 DB 로드
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    return vectorstore


def create_bm25_index(chunks: List[Document], bm25_path: str = None) -> BM25Okapi:
    """
    BM25 인덱스 생성 및 저장
    
    Args:
        chunks: 청크된 문서 리스트
        bm25_path: 저장 경로
        
    Returns:
        BM25Okapi 인덱스
    """
    # 텍스트를 토큰화 (공백 기준)
    tokenized_corpus = [doc.page_content.split() for doc in chunks]
    
    # BM25 인덱스 생성
    bm25 = BM25Okapi(tokenized_corpus)
    
    # pickle로 저장
    if bm25_path:
        os.makedirs(os.path.dirname(bm25_path), exist_ok=True)
        with open(bm25_path, 'wb') as f:
            # chunks와 bm25를 함께 저장
            pickle.dump({'bm25': bm25, 'chunks': chunks}, f)
    
    return bm25


def load_bm25_index(bm25_path: str) -> tuple:
    """
    BM25 인덱스 로드
    
    Args:
        bm25_path: 저장 경로
        
    Returns:
        (BM25Okapi, List[Document])
    """
    with open(bm25_path, 'rb') as f:
        data = pickle.load(f)
    
    return data['bm25'], data['chunks']


def hybrid_search(
    query: str, 
    vectorstore: Chroma, 
    bm25: BM25Okapi, 
    bm25_chunks: List[Document],
    config: Dict
) -> List[Document]:
    """
    벡터 + BM25 하이브리드 검색 (RRF로 결합)
    
    Args:
        query: 검색 쿼리
        vectorstore: ChromaDB 벡터스토어
        bm25: BM25 인덱스
        bm25_chunks: BM25에 대응하는 문서 리스트
        config: config.yaml의 retrieval 설정
        
    Returns:
        최종 검색 결과 문서 리스트
    """
    try:
        vector_top_k = config['retrieval']['vector_top_k']
        bm25_top_k = config['retrieval']['bm25_top_k']
        final_top_k = config['retrieval']['final_top_k']
        
        # 1. 벡터 검색
        vector_results = vectorstore.similarity_search(query, k=vector_top_k)
        
        # 2. BM25 검색
        import numpy as np
        tokenized_query = query.split()
        bm25_scores = bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:bm25_top_k]
        
        bm25_results = []
        for idx in bm25_indices:
            if idx < len(bm25_chunks) and bm25_scores[idx] > 0:
                bm25_results.append(bm25_chunks[idx])
        
        # 3. 결과 병합 (중복 제거)
        seen_contents = set()
        combined_results = []
        
        # 벡터 검색 결과 우선
        for doc in vector_results:
            content_hash = hash(doc.page_content[:200])
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                combined_results.append(doc)
        
        # BM25 결과 추가
        for doc in bm25_results:
            content_hash = hash(doc.page_content[:200])
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                combined_results.append(doc)
        
        # 최종 top_k만 반환
        final_results = combined_results[:final_top_k]
        
        return final_results
    
    except Exception as e:
        print(f"[ERROR] 검색 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def check_database_exists(chroma_path: str, bm25_path: str) -> bool:
    """
    기존 DB 존재 여부 확인
    
    Args:
        chroma_path: ChromaDB 경로
        bm25_path: BM25 인덱스 경로
        
    Returns:
        존재 여부
    """
    chroma_exists = os.path.exists(chroma_path) and os.listdir(chroma_path)
    bm25_exists = os.path.exists(bm25_path)
    
    return chroma_exists and bm25_exists
