# 학교 행정매뉴얼 RAG 챗봇 개발 계획

## 프로젝트 개요

**목표**: "2025 학교 업무매뉴얼 행정(최종).pdf"를 소스로 하는 정확도 중심 RAG 챗봇 개발

**핵심 스펙**:
- **LLM**: GPT-4o mini
- **임베딩**: OpenAI text-embedding-3-small
- **인터페이스**: Streamlit 웹앱
- **배포**: Streamlit Cloud
- **사용자**: 2-3명
- **답변 형식**: 질문요지정리 → 절차 → 관련법령 → 서식 → 주의사항

---

## 기술 스택

### 핵심 라이브러리
- **PDF 파싱**: PyMuPDF (fitz)
- **임베딩/LLM**: OpenAI API (text-embedding-3-small, gpt-4o-mini)
- **벡터 DB**: ChromaDB (영구 저장)
- **검색**: Hybrid (Vector + BM25)
- **프레임워크**: LangChain, Streamlit
- **기타**: rank-bm25, python-dotenv, PyYAML

### 인프라
- **배포**: Streamlit Cloud
- **DB 저장**: GitHub 리포지토리 (`./data/` 폴더 커밋)
- **환경변수**: Streamlit Secrets (OPENAI_API_KEY, ADMIN_PASSWORD)

---

## 프로젝트 구조

```
chatbot/
├── 2025 학교 업무매뉴얼 행정(최종).pdf
├── .env                          # API 키, 비밀번호 (로컬, .gitignore)
├── .env.example                  # 환경변수 템플릿
├── .gitignore                    # .env, __pycache__, *.pyc 제외
├── requirements.txt              # 의존성 목록
├── config.yaml                   # 청킹/검색 파라미터
├── README.md                     # 사용법, 배포 가이드
├── PLAN.md                       # 프로젝트 계획서
├── PROCEED.md                    # 실행 절차 가이드
├── app.py                        # Streamlit 메인 앱
│
├── .streamlit/
│   └── config.toml               # Streamlit 테마/서버 설정
│
├── data/                         # 벡터 DB (GitHub 커밋)
│   ├── chroma_db/                # ChromaDB 영구 저장소
│   └── bm25_index.pkl            # BM25 인덱스
│
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py          # PDF 파싱 및 청킹
│   ├── vectorstore.py            # 벡터 DB 관리
│   ├── rag_chain.py              # RAG 체인 및 프롬프트
│   └── response_formatter.py     # 답변 구조화
│
├── scripts/
│   ├── analyze_pdf.py            # PDF 구조 분석 도구
│   └── create_database.py        # 초기 DB 생성 스크립트
│
└── tests/
    ├── test_queries.txt          # 테스트 질문 목록
    └── evaluate.py               # 자동 평가 스크립트
```

---

## 상세 구현 단계

### 1단계: PDF 구조 분석 (사전 조사)

**파일**: `scripts/analyze_pdf.py`

**목적**: 실제 PDF 구조를 파악하여 청킹 전략 최적화

**구현 내용**:
- PyMuPDF로 PDF 로드
- 총 페이지 수, 파일 크기, 메타데이터 추출
- 제목/섹션 계층 구조 분석:
  - 로마숫자 대분류 (Ⅰ., Ⅱ., Ⅲ.)
  - 아라비아숫자 중분류 (1., 2., 3.)
  - 하이픈/점 소분류 (1-1, 1-2 또는 1.1, 1.2)
- 텍스트 밀도 측정 (페이지당 평균 문자 수)
- 특수 요소 탐지 (표, 목록, 법령 인용, 서식 번호)
- 청킹 전략 제안 (정규식 패턴, 적정 청크 크기)

**출력**: 콘솔에 상세 분석 보고서 출력

---

### 2단계: 프로젝트 설정 파일 생성

#### 2-1. `.gitignore`

```gitignore
# 환경 변수
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# 가상환경
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml

# 임시 파일
*.log
*.tmp
```

#### 2-2. `.env.example`

```bash
# OpenAI API 키
OPENAI_API_KEY=sk-your-api-key-here

# 관리자 비밀번호 (DB 갱신용)
ADMIN_PASSWORD=your-secure-password-here
```

#### 2-3. `requirements.txt`

```
# PDF 처리
PyMuPDF==1.23.8

# OpenAI
openai==1.12.0

# LangChain
langchain==0.1.6
langchain-community==0.0.20
langchain-openai==0.0.5

# 벡터 DB
chromadb==0.4.22

# 검색
rank-bm25==0.2.2

# 웹 프레임워크
streamlit==1.31.0

# 유틸리티
python-dotenv==1.0.1
PyYAML==6.0.1
tqdm==4.66.1
```

#### 2-4. `config.yaml`

```yaml
# PDF 처리 설정
pdf:
  source_file: "2025 학교 업무매뉴얼 행정(최종).pdf"

# 청킹 설정
chunking:
  chunk_size: 1200          # 토큰 수 기준
  chunk_overlap: 150        # 오버랩 토큰 수
  separators:
    - "\n\n\n"              # 대분류 구분
    - "\n\n"                # 중분류 구분
    - "\n"                  # 소분류 구분
    - ". "                  # 문장
    - " "                   # 단어

# 임베딩 설정
embedding:
  model: "text-embedding-3-small"
  dimensions: 1536

# LLM 설정
llm:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 1500

# 검색 설정
retrieval:
  vector_top_k: 10
  bm25_top_k: 10
  final_top_k: 5
  
# 벡터 DB 경로
database:
  chroma_path: "./data/chroma_db"
  bm25_path: "./data/bm25_index.pkl"
```

---

### 3단계: PDF 파싱 및 청킹 모듈

**파일**: `src/pdf_processor.py`

**핵심 기능**:

1. **PDF 텍스트 추출**
   ```python
   def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
       """PDF에서 페이지별 텍스트 추출"""
   ```

2. **계층 구조 파싱**
   ```python
   def parse_hierarchy(text: str) -> Dict:
       """정규식으로 섹션 계층 추출"""
       # 패턴:
       # - 로마숫자: r'^([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)\.\s*(.+)$'
       # - 숫자: r'^(\d+)\.\s+([가-힣].+)$'
       # - 하이픈: r'^(\d+-\d+)\s+(.+)$'
   ```

3. **메타데이터 추출**
   ```python
   def extract_metadata(chunk_text: str, page_num: int) -> Dict:
       """법령, 서식 번호 등 추출"""
       # 법령: r'(제\s*\d+조|[가-힣]+법\s*제|시행령|시행규칙)'
       # 서식: r'서식\s*\d+|<서식|【서식'
   ```

4. **청킹 처리**
   ```python
   def chunk_documents(documents: List[Document], config: Dict) -> List[Document]:
       """RecursiveCharacterTextSplitter 사용"""
       # config.yaml의 청킹 설정 적용
       # 메타데이터 보강 (섹션 경로, 페이지, 법령, 서식)
   ```

5. **예외 처리**
   - 파일 없음 → `FileNotFoundError`
   - PDF 암호화 → 에러 메시지 출력
   - 텍스트 추출 실패 → 빈 문자열 처리 및 로그

---

### 4단계: 벡터 스토어 모듈

**파일**: `src/vectorstore.py`

**핵심 기능**:

1. **ChromaDB 초기화**
   ```python
   def create_vectorstore(chunks: List[Document], config: Dict) -> Chroma:
       """ChromaDB 생성 및 저장"""
       # OpenAI 임베딩 사용
       # persist_directory 설정으로 영구 저장
   ```

2. **BM25 인덱스 생성**
   ```python
   def create_bm25_index(chunks: List[Document]) -> BM25Okapi:
       """키워드 검색용 BM25 인덱스"""
       # pickle로 저장
   ```

3. **하이브리드 검색**
   ```python
   def hybrid_search(query: str, vector_top_k: int, bm25_top_k: int) -> List[Document]:
       """벡터 + BM25 검색 결과 RRF로 결합"""
       # Reciprocal Rank Fusion 알고리즘
   ```

4. **DB 존재 확인**
   ```python
   def check_database_exists(chroma_path: str, bm25_path: str) -> bool:
       """기존 DB 존재 여부 확인"""
   ```

5. **예외 처리**
   - API 키 누락 → `ValueError`
   - 네트워크 오류 → `requests.exceptions.RequestException`
   - 임베딩 실패 → 재시도 로직 (최대 3회)

---

### 5단계: 초기 DB 생성 스크립트

**파일**: `scripts/create_database.py`

**실행 흐름**:
1. `config.yaml` 로드
2. PDF 파싱 (`pdf_processor.py`)
3. 청킹 수행
4. 진행률 표시 (`tqdm`)
5. ChromaDB 생성 및 저장
6. BM25 인덱스 생성 및 저장
7. 성공 로그 출력

**안전장치**:
- 기존 DB 존재 시 백업 생성 (timestamp 폴더)
- 실행 전 확인 프롬프트

**실행 방법**:
```bash
python scripts/create_database.py
```

---

### 6단계: RAG 체인 및 프롬프트

**파일**: `src/rag_chain.py`

**핵심 기능**:

1. **쿼리 처리**
   ```python
   def process_query(query: str, vectorstore, bm25_index, config: Dict) -> str:
       """전체 RAG 파이프라인"""
   ```

2. **검색 단계**
   - 하이브리드 검색 (벡터 top-10 + BM25 top-10)
   - RRF로 최종 top-5 선택

3. **프롬프트 구성**
   ```python
   SYSTEM_PROMPT = """
   당신은 학교 행정 업무 전문가입니다.
   
   **역할**:
   - "2025 학교 업무매뉴얼 행정" 기반으로 정확한 답변 제공
   - 추측하지 않고 문서에 있는 내용만 답변
   - 답변 형식을 반드시 준수
   
   **답변 형식** (필수):
   
   ### ① 질문 요지 정리
   [사용자 질문을 명확히 요약]
   
   ### ② 절차
   [단계별 처리 절차를 순서대로 설명]
   
   ### ③ 관련 법령
   [관련 법령, 조항, 시행령 등을 명시]
   
   ### ④ 서식
   [필요한 서식 번호 및 명칭]
   
   ### ⑤ 주의사항
   [반드시 유의해야 할 사항]
   
   ### 📄 출처
   [참조한 섹션명과 페이지 번호]
   
   **중요**:
   - 문서에 없는 내용은 "문서에서 관련 내용을 찾을 수 없습니다"라고 명시
   - 법령이나 서식이 없는 경우 "해당 없음"으로 표시
   """
   ```

4. **GPT-4o mini 호출**
   ```python
   def call_llm(prompt: str, context: str, config: Dict) -> str:
       """OpenAI API 호출"""
       # 온도: 0.1 (정확성 우선)
       # max_tokens: 1500
   ```

5. **예외 처리**
   - 검색 결과 없음 → "관련 정보를 찾을 수 없습니다" 반환
   - API 할당량 초과 → 에러 메시지 및 재시도 안내
   - 타임아웃 → 30초 제한, 초과 시 재시도

---

### 7단계: 답변 포맷터

**파일**: `src/response_formatter.py`

**핵심 기능**:

1. **구조 검증**
   ```python
   def validate_response_structure(response: str) -> bool:
       """5단계 구조 존재 여부 확인"""
       required_sections = [
           "① 질문 요지 정리",
           "② 절차",
           "③ 관련 법령",
           "④ 서식",
           "⑤ 주의사항"
       ]
   ```

2. **출처 추가**
   ```python
   def add_sources(response: str, retrieved_docs: List[Document]) -> str:
       """검색된 문서의 메타데이터로 출처 섹션 추가"""
   ```

3. **마크다운 변환**
   ```python
   def format_to_markdown(response: str) -> str:
       """Streamlit 렌더링용 마크다운 정리"""
   ```

4. **답변 없음 처리**
   ```python
   def no_answer_message() -> str:
       """검색 결과 없을 때 안내 메시지"""
   ```

---

### 8단계: Streamlit 웹앱

**파일**: `app.py`

**UI 구성**:

#### 메인 화면
```python
import streamlit as st

st.set_page_config(
    page_title="학교 업무매뉴얼 챗봇",
    page_icon="🏫",
    layout="wide"
)

st.title("🏫 학교 행정업무 챗봇")
st.caption("2025 학교 업무매뉴얼 행정 기반 AI 도우미")
```

#### 채팅 인터페이스
```python
# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 이력 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("궁금한 업무에 대해 질문해주세요"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # RAG 체인 실행
    with st.spinner("답변 생성 중..."):
        response = process_query(prompt, vectorstore, bm25_index, config)
    
    # 어시스턴트 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
```

#### 사이드바
```python
with st.sidebar:
    st.header("⚙️ 설정")
    
    # API 키 입력
    api_key = st.text_input(
        "OpenAI API 키",
        type="password",
        value=st.secrets.get("OPENAI_API_KEY", "")
    )
    
    # 검색 설정
    st.subheader("검색 설정")
    top_k = st.slider("검색 결과 수", 3, 10, 5)
    
    # 대화 초기화
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()
```

#### DB 갱신 섹션 (관리자 전용)
```python
with st.sidebar:
    st.divider()
    
    with st.expander("🔧 데이터베이스 갱신 (관리자)"):
        admin_password = st.text_input(
            "관리자 비밀번호",
            type="password",
            key="admin_pw"
        )
        
        uploaded_file = st.file_uploader(
            "새 PDF 업로드",
            type=["pdf"]
        )
        
        if st.button("🔄 데이터베이스 갱신"):
            # 비밀번호 검증
            if admin_password != st.secrets.get("ADMIN_PASSWORD", ""):
                st.error("❌ 비밀번호가 일치하지 않습니다.")
            elif not uploaded_file:
                st.error("❌ PDF 파일을 업로드해주세요.")
            else:
                with st.spinner("데이터베이스 갱신 중..."):
                    try:
                        # PDF 저장
                        # DB 재생성
                        # 성공 메시지
                        st.success("✅ 데이터베이스가 갱신되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 오류: {str(e)}")
```

#### DB 자동 로드
```python
@st.cache_resource
def load_vectorstore():
    """벡터 DB 로드 (캐싱)"""
    if not check_database_exists(chroma_path, bm25_path):
        st.error("⚠️ 데이터베이스가 없습니다. 관리자에게 문의하세요.")
        st.stop()
    
    try:
        vectorstore = load_chroma(chroma_path)
        bm25_index = load_bm25(bm25_path)
        return vectorstore, bm25_index
    except Exception as e:
        st.error(f"❌ DB 로드 오류: {str(e)}")
        st.stop()
```

#### 예외 처리 (Toast 알림)
```python
try:
    response = process_query(prompt, vectorstore, bm25_index, config)
except openai.RateLimitError:
    st.toast("⚠️ API 사용량 초과. 잠시 후 다시 시도해주세요.", icon="⚠️")
except openai.APIError as e:
    st.toast(f"❌ API 오류: {str(e)}", icon="❌")
except Exception as e:
    st.toast(f"❌ 예상치 못한 오류: {str(e)}", icon="❌")
```

---

### 9단계: 테스트 케이스

**파일**: `tests/test_queries.txt`

```
# 학교 행정업무 챗봇 테스트 질문

1. 공문서 접수 절차는 어떻게 되나요?
2. 예산 집행 시 주의사항은 무엇인가요?
3. 교원 인사 발령은 어떤 절차로 진행되나요?
4. 학생 전학 처리 방법을 알려주세요.
5. 학교운영위원회 소집 절차는?
6. 급식비 지원 관련 서류는 무엇이 필요한가요?
7. 시설 안전점검 주기와 방법은?
8. 교육과정 편성 시 법적 근거는?
9. 학생 상담 기록 보관 기간은?
10. 교직원 복무 관리 규정은?
11. 학교 회계 결산 시기와 절차는?
12. 학생 징계 처리 절차를 알려주세요.
13. 외부 강사 계약 시 필요한 서식은?
14. 교육활동 침해 대응 절차는?
15. 학교 예산 편성 시 유의사항은?
```

**파일**: `tests/evaluate.py`

```python
"""자동 평가 스크립트"""
import sys
sys.path.append('..')

from src.rag_chain import process_query
from src.vectorstore import load_vectorstore
import yaml

def evaluate_queries(test_file: str):
    """테스트 질문으로 평가"""
    
    # DB 로드
    vectorstore, bm25_index = load_vectorstore()
    
    # 설정 로드
    with open('../config.yaml') as f:
        config = yaml.safe_load(f)
    
    # 질문 로드
    with open(test_file) as f:
        queries = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"질문 {i}: {query}")
        print('='*80)
        
        try:
            response = process_query(query, vectorstore, bm25_index, config)
            print(response)
            
            # 구조 검증
            has_all_sections = all(
                section in response
                for section in ["①", "②", "③", "④", "⑤"]
            )
            
            results.append({
                "query": query,
                "success": True,
                "has_structure": has_all_sections
            })
            
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # 결과 요약
    print(f"\n\n{'='*80}")
    print("평가 결과 요약")
    print('='*80)
    success_count = sum(1 for r in results if r["success"])
    structure_count = sum(1 for r in results if r.get("has_structure", False))
    
    print(f"총 질문 수: {len(queries)}")
    print(f"성공: {success_count}/{len(queries)} ({success_count/len(queries)*100:.1f}%)")
    print(f"구조 준수: {structure_count}/{len(queries)} ({structure_count/len(queries)*100:.1f}%)")

if __name__ == "__main__":
    evaluate_queries("test_queries.txt")
```

---

### 10단계: 배포 준비

#### 10-1. `README.md`

```markdown
# 🏫 학교 행정업무 챗봇

2025 학교 업무매뉴얼 행정 문서 기반 AI 챗봇입니다.

## 기능

- ✅ 학교 행정 업무 질의응답
- ✅ 구조화된 답변 (질문요지-절차-법령-서식-주의사항)
- ✅ 정확한 출처 표시 (섹션, 페이지)
- ✅ 관리자 전용 DB 갱신 기능

## 로컬 실행 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd chatbot
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 API 키와 비밀번호 입력
```

### 5. 데이터베이스 생성 (최초 1회)
```bash
python scripts/create_database.py
```

### 6. 앱 실행
```bash
streamlit run app.py
```

## Streamlit Cloud 배포

### 1. GitHub 리포지토리 푸시
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Streamlit Cloud 설정
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. "New app" 클릭
3. GitHub 리포지토리 연결
4. Main file: `app.py`
5. Python version: 3.10

### 3. Secrets 설정
Streamlit Cloud 대시보드 > Settings > Secrets에서:

```toml
OPENAI_API_KEY = "sk-your-api-key"
ADMIN_PASSWORD = "your-secure-password"
```

### 4. 배포
"Deploy" 버튼 클릭

## 사용 방법

1. 웹앱 접속
2. 사이드바에서 API 키 입력 (또는 Secrets 자동 로드)
3. 질문 입력창에 업무 관련 질문 입력
4. 구조화된 답변 확인

## DB 갱신 방법 (관리자)

1. 사이드바 하단 "데이터베이스 갱신" 섹션 펼치기
2. 관리자 비밀번호 입력
3. 새 PDF 파일 업로드
4. "데이터베이스 갱신" 버튼 클릭

## 기술 스택

- **LLM**: GPT-4o mini
- **임베딩**: text-embedding-3-small
- **벡터 DB**: ChromaDB
- **검색**: Hybrid (Vector + BM25)
- **프레임워크**: LangChain, Streamlit

## 라이선스

MIT License
```

#### 10-2. `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#4A90E2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 50
```

---

## 비용 산정

### 초기 비용 (1회)
- **임베딩**: 200페이지 PDF, 약 150,000 토큰
- **비용**: $0.003 - $0.005

### 월간 운영 비용 (2-3명 사용)
- **쿼리 임베딩**: 월 100회 × 평균 20 토큰 = 2,000 토큰 → $0.00004
- **LLM 응답**: 월 100회 × (입력 1,500 토큰 + 출력 500 토큰)
  - 입력: 100 × 1,500 = 150,000 토큰 → $0.02
  - 출력: 100 × 500 = 50,000 토큰 → $0.03
- **총 월간 비용**: 약 $0.05 - $0.10 (월 1,000원 미만)

### 연간 비용
- **DB 갱신**: 연 1회 × $0.005 = $0.005
- **사용 비용**: 12개월 × $0.10 = $1.20
- **총 연간 비용**: 약 $1.20 - $2.00 (연 2,500원 내외)

---

## 보안 고려사항

### 1. API 키 관리
- ✅ `.env` 파일 `.gitignore`에 추가
- ✅ Streamlit Secrets 사용 (배포 시)
- ✅ 코드에 하드코딩 절대 금지

### 2. 관리자 비밀번호
- ✅ 최소 12자 이상
- ✅ 영문 대소문자 + 숫자 + 특수문자 조합
- ✅ 환경변수로 관리
- ✅ 예시: `Adm1n!2025@School#`

### 3. DB 갱신 권한
- ✅ 비밀번호 인증 필수
- ✅ UI에서 expander로 숨김 처리
- ✅ 잘못된 비밀번호 입력 시 에러 메시지만 표시

---

## 유지보수 계획

### 연간 작업 (매년 1월)
1. 새 PDF 파일 업로드
2. 관리자 페이지에서 DB 갱신
3. 테스트 질문으로 검증
4. 필요시 청킹 파라미터 조정

### 모니터링
- Streamlit Cloud 대시보드에서 앱 상태 확인
- OpenAI 사용량 대시보드에서 비용 모니터링
- 사용자 피드백 수집

---

## 문제 해결

### Q1. "데이터베이스를 찾을 수 없습니다" 오류
**해결**: `scripts/create_database.py` 실행 후 `data/` 폴더를 GitHub에 커밋

### Q2. API 키 오류
**해결**: `.env` 또는 Streamlit Secrets에서 `OPENAI_API_KEY` 확인

### Q3. 답변이 부정확함
**해결**:
- `config.yaml`에서 `retrieval.final_top_k` 증가 (5 → 7)
- `llm.temperature` 감소 (0.1 → 0.05)
- 테스트 후 재평가

### Q4. DB 갱신 실패
**해결**:
- PDF 파일이 암호화되지 않았는지 확인
- 파일 크기 50MB 이하 확인
- 로그에서 구체적 오류 메시지 확인

---

## 다음 개선 방향 (선택)

1. **Cross-Encoder 재순위화**: 검색 정확도 추가 향상
2. **대화 컨텍스트 유지**: 이전 질문 참조 기능
3. **사용 통계**: 질문 빈도 분석 대시보드
4. **다중 PDF 지원**: 여러 매뉴얼 통합 검색
5. **음성 입력**: Whisper API 연동

---

## 추가 고려사항 반영 체크리스트

### ✅ API 키 관리
- [x] `.env.example` 파일 생성
- [x] `.gitignore`에 `.env` 추가
- [x] Streamlit Secrets 가이드 작성

### ✅ 배포 방식
- [x] Streamlit Cloud 배포 가이드
- [x] `.streamlit/config.toml` 설정
- [x] Secrets 등록 방법 문서화

### ✅ 초기 데이터베이스
- [x] `create_database.py` 스크립트
- [x] 최초 1회 실행 안내
- [x] `data/` 폴더 GitHub 커밋 전략

### ✅ DB 갱신 기능
- [x] `app.py`에 갱신 UI 추가
- [x] 관리자 비밀번호 검증
- [x] PDF 업로드 기능
- [x] 진행률 표시

### ✅ 에러 처리
- [x] 파일 없음 예외
- [x] API 호출 실패 처리
- [x] 네트워크 오류 처리
- [x] 검색 결과 없음 처리
- [x] Toast 알림 UI

### ✅ GitHub 관리
- [x] `.gitignore` 작성
- [x] `data/` 폴더 포함
- [x] README 작성

---

## 구현 순서 요약

1. **분석**: `analyze_pdf.py` 실행
2. **설정**: `.gitignore`, `.env`, `requirements.txt`, `config.yaml`
3. **핵심 모듈**: `pdf_processor.py`, `vectorstore.py`, `rag_chain.py`
4. **DB 생성**: `create_database.py` 실행
5. **웹앱**: `app.py` 개발
6. **테스트**: `evaluate.py`로 검증
7. **배포**: GitHub 푸시 → Streamlit Cloud 연결

---

**예상 개발 시간**: 8-12시간  
**첫 배포까지**: 1-2일
