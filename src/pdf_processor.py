"""
PDF 처리 모듈
- PDF 텍스트 추출
- 계층 구조 파싱
- 메타데이터 추출
- 청킹 처리
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    PDF에서 페이지별 텍스트 추출
    
    Args:
        pdf_path: PDF 파일 경로
        
    Returns:
        페이지별 텍스트 리스트 [{"page": 1, "text": "..."}]
    """
    try:
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            pages_data.append({
                "page": page_num,
                "text": text
            })
        
        doc.close()
        return pages_data
    
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
    except Exception as e:
        raise Exception(f"PDF 처리 중 오류 발생: {str(e)}")


def parse_hierarchy(text: str) -> Dict:
    """
    정규식으로 섹션 계층 추출
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        계층 정보 딕셔너리
    """
    hierarchy = {
        "level1": None,  # 로마숫자 (Ⅰ, Ⅱ, Ⅲ)
        "level2": None,  # 숫자 (1, 2, 3)
        "level3": None   # 하이픈/점 (1-1, 1.1)
    }
    
    # 로마숫자 대분류 패턴
    roman_pattern = r'^([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)\.\s*(.+)$'
    roman_match = re.search(roman_pattern, text, re.MULTILINE)
    if roman_match:
        hierarchy["level1"] = roman_match.group(2).strip()
    
    # 아라비아숫자 중분류 패턴
    number_pattern = r'^(\d+)\.\s+([가-힣].+)$'
    number_match = re.search(number_pattern, text, re.MULTILINE)
    if number_match:
        hierarchy["level2"] = number_match.group(2).strip()
    
    # 하이픈 소분류 패턴
    hyphen_pattern = r'^(\d+-\d+)\s+(.+)$'
    hyphen_match = re.search(hyphen_pattern, text, re.MULTILINE)
    if hyphen_match:
        hierarchy["level3"] = hyphen_match.group(2).strip()
    
    return hierarchy


def extract_metadata(chunk_text: str, page_num: int) -> Dict:
    """
    법령, 서식 번호 등 메타데이터 추출
    
    Args:
        chunk_text: 청크 텍스트
        page_num: 페이지 번호
        
    Returns:
        메타데이터 딕셔너리
    """
    metadata = {
        "page": page_num,
        "laws": [],
        "forms": []
    }
    
    # 법령 패턴
    law_patterns = [
        r'제\s*\d+조',
        r'[가-힣]+법\s*제',
        r'시행령',
        r'시행규칙'
    ]
    
    for pattern in law_patterns:
        matches = re.findall(pattern, chunk_text)
        metadata["laws"].extend(matches)
    
    # 서식 패턴
    form_patterns = [
        r'서식\s*\d+',
        r'<서식[^>]*>',
        r'【서식[^】]*】'
    ]
    
    for pattern in form_patterns:
        matches = re.findall(pattern, chunk_text)
        metadata["forms"].extend(matches)
    
    # 중복 제거
    metadata["laws"] = list(set(metadata["laws"]))
    metadata["forms"] = list(set(metadata["forms"]))
    
    return metadata


def chunk_documents(documents: List[Document], config: Dict) -> List[Document]:
    """
    RecursiveCharacterTextSplitter로 청킹 및 메타데이터 보강
    
    Args:
        documents: 원본 문서 리스트
        config: config.yaml의 chunking 설정
        
    Returns:
        청크된 문서 리스트
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['chunk_size'],
        chunk_overlap=config['chunk_overlap'],
        separators=config['separators'],
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # 메타데이터 보강 및 정리
    for chunk in chunks:
        page_num = chunk.metadata.get('page', 0)
        
        # 계층 정보 추가
        hierarchy = parse_hierarchy(chunk.page_content)
        
        # None 값 제거 및 문자열로 변환
        for key, value in hierarchy.items():
            if value is not None:
                chunk.metadata[key] = str(value)
        
        # 법령/서식 정보 추가
        extracted_meta = extract_metadata(chunk.page_content, page_num)
        
        # 리스트를 문자열로 변환
        if extracted_meta['laws']:
            chunk.metadata['laws'] = ', '.join(extracted_meta['laws'])
        
        if extracted_meta['forms']:
            chunk.metadata['forms'] = ', '.join(extracted_meta['forms'])
    
    return chunks


def process_pdf(pdf_path: str, config: Dict) -> List[Document]:
    """
    PDF 전체 처리 파이프라인
    
    Args:
        pdf_path: PDF 파일 경로
        config: config.yaml 설정
        
    Returns:
        청크된 문서 리스트
    """
    # 1. 텍스트 추출
    pages_data = extract_text_from_pdf(pdf_path)
    
    # 2. Document 객체로 변환
    documents = []
    for page_data in pages_data:
        doc = Document(
            page_content=page_data['text'],
            metadata={"page": page_data['page']}
        )
        documents.append(doc)
    
    # 3. 청킹
    chunks = chunk_documents(documents, config['chunking'])
    
    return chunks
