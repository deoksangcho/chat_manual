"""
초기 데이터베이스 생성 스크립트
- PDF 파싱
- 청킹
- ChromaDB 및 BM25 인덱스 생성
"""

import sys
import os
import time
import yaml
from datetime import datetime
from dotenv import load_dotenv

# 상위 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_processor import process_pdf
from src.vectorstore import create_vectorstore, create_bm25_index, check_database_exists
from tqdm import tqdm


def load_config() -> dict:
    """config.yaml 로드"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    print("=" * 80)
    print("학교 행정매뉴얼 데이터베이스 생성")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    # 환경변수 로드
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 API 키를 추가해 주세요.")
        sys.exit(1)
    
    # 1. config.yaml 로드
    print("[1/6] config.yaml 로드 중... ", end='')
    try:
        config = load_config()
        print("✓")
    except Exception as e:
        print(f"✗\n❌ 오류: {e}")
        sys.exit(1)
    
    # 2. PDF 파일 확인
    pdf_path = config['pdf']['source_file']
    print(f"[2/6] PDF 파일 확인 중... ", end='')
    
    if not os.path.exists(pdf_path):
        print(f"✗\n❌ 오류: PDF 파일을 찾을 수 없습니다: {pdf_path}")
        sys.exit(1)
    
    print("✓")
    
    # 3. 기존 DB 확인
    chroma_path = config['database']['chroma_path']
    bm25_path = config['database']['bm25_path']
    
    if check_database_exists(chroma_path, bm25_path):
        print()
        print("⚠️  경고: 기존 데이터베이스가 발견되었습니다.")
        print(f"   - ChromaDB: {chroma_path}")
        print(f"   - BM25: {bm25_path}")
        
        response = input("   덮어쓰시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("   취소되었습니다.")
            sys.exit(0)
        
        # 백업 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"./data/backup_{timestamp}"
        print(f"   기존 DB를 백업합니다: {backup_dir}")
        
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(chroma_path):
            import shutil
            shutil.move(chroma_path, os.path.join(backup_dir, "chroma_db"))
        
        if os.path.exists(bm25_path):
            import shutil
            shutil.move(bm25_path, os.path.join(backup_dir, "bm25_index.pkl"))
        
        print("   ✓ 백업 완료")
        print()
    
    # 4. PDF 파싱 및 청킹
    print("[3/6] PDF 파싱 및 청킹 중...")
    try:
        chunks = process_pdf(pdf_path, config)
        print(f"      ✓ 총 {len(chunks)}개 청크 생성")
    except Exception as e:
        print(f"      ✗ 오류: {e}")
        sys.exit(1)
    
    # 5. ChromaDB 생성
    print("[4/6] ChromaDB 생성 중...")
    try:
        # 진행률 표시를 위한 tqdm (실제로는 임베딩 생성 중)
        vectorstore = create_vectorstore(chunks, config)
        print(f"      ✓ 저장 경로: {chroma_path}")
    except Exception as e:
        print(f"      ✗ 오류: {e}")
        sys.exit(1)
    
    # 6. BM25 인덱스 생성
    print("[5/6] BM25 인덱스 생성 중... ", end='')
    try:
        bm25 = create_bm25_index(chunks, bm25_path)
        print("✓")
        print(f"      저장 경로: {bm25_path}")
    except Exception as e:
        print(f"✗\n      오류: {e}")
        sys.exit(1)
    
    # 완료
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print()
    print("=" * 80)
    print("✅ 데이터베이스 생성 완료!")
    print("=" * 80)
    print(f"총 소요 시간: {minutes}분 {seconds}초")
    print(f"총 청크 수: {len(chunks)}개")
    print()
    print("다음 단계:")
    print("  1. 로컬 테스트: streamlit run app.py")
    print("  2. GitHub 푸시 후 Streamlit Cloud 배포")
    print()


if __name__ == "__main__":
    main()
