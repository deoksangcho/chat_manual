# 🏫 학교 행정매뉴얼 RAG 챗봇

**2025 학교 업무매뉴얼 행정** 기반 질의응답 시스템

## 📋 프로젝트 개요

학교 행정 업무 담당자를 위한 AI 챗봇입니다. 416페이지 분량의 학교 업무매뉴얼을 기반으로 정확하고 상세한 답변을 제공합니다.

### 주요 기능

- 📚 **하이브리드 검색**: Vector(의미 기반) + BM25(키워드 기반)
- 🤖 **GPT-4o mini**: 최신 OpenAI 모델 사용
- 📊 **구조화된 답변**: 질문 요지 → 절차 → 법령 → 서식 → 주의사항 → 출처
- 🔒 **보안**: API 키 Streamlit Secrets로 안전하게 관리
- 💾 **468개 청크**: ChromaDB 벡터 저장소

## 🚀 빠른 시작

### 로컬 실행

```bash
# 1. 저장소 클론
git clone https://github.com/deoksangcho/chat_manual.git
cd chat_manual

# 2. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. API 키 설정
# .env 파일 생성하고 OpenAI API 키 입력
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 5. 앱 실행
streamlit run app.py
```

### 데이터베이스 재생성 (선택사항)

```bash
python scripts/create_database.py
```

## ☁️ Streamlit Cloud 배포

### 1단계: Streamlit Cloud 접속

1. https://share.streamlit.io/ 접속
2. GitHub 계정으로 로그인

### 2단계: New app 생성

1. **New app** 버튼 클릭
2. 다음 정보 입력:
   - **Repository**: `deoksangcho/chat_manual`
   - **Branch**: `main`
   - **Main file path**: `app.py`

### 3단계: Secrets 설정

**Advanced settings** > **Secrets** 클릭 후 다음 내용 입력:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### 4단계: Deploy

**Deploy!** 버튼 클릭

배포 완료까지 약 5-10분 소요됩니다.

## 🛠️ 기술 스택

### AI/ML
- **LLM**: OpenAI GPT-4o mini
- **Embedding**: text-embedding-3-small (1536 dimensions)
- **Vector DB**: ChromaDB 0.4.22
- **Keyword Search**: BM25Okapi

### 프레임워크
- **Web**: Streamlit 1.31.0
- **RAG**: LangChain 0.1.6
- **PDF**: PyMuPDF 1.23.8

### 설정

**config.yaml**:
```yaml
chunking:
  chunk_size: 1500
  chunk_overlap: 200

retrieval:
  vector_top_k: 12
  bm25_top_k: 12
  final_top_k: 10

llm:
  model: "gpt-4o-mini"
  temperature: 0.0
  max_tokens: 3000
```

## 📊 성능 지표

- **문서 크기**: 416 페이지 (9.34 MB)
- **청크 수**: 468개
- **검색 시간**: ~1-2초
- **응답 생성**: ~3-5초
- **컨텍스트**: 최대 10개 문서

## 📖 사용 예시

**질문 예시**:
- 공문서 접수 절차는 어떻게 되나요?
- 징계대상자 급여 감액 비율은?
- 예산 집행 시 주의사항은?
- 근무성적평정 관련 법령은?

**답변 구조**:
1. ① 질문 요지 정리
2. ② 절차 (단계별 상세 설명)
3. ③ 관련 법령 (조문 내용 + 실무 적용)
4. ④ 서식 (번호, 작성법, 제출처)
5. ⑤ 주의사항 (실수 사례, 예외 상황, 실무 팁)
6. 📄 출처 (페이지 번호 포함)

## 🔧 문제 해결

### API 키 오류
```
⚠️ OpenAI API 키를 입력해 주세요
```
→ `.env` 파일 또는 Streamlit Secrets에 API 키 설정 확인

### 데이터베이스 없음
```
❌ 데이터베이스를 찾을 수 없습니다
```
→ `python scripts/create_database.py` 실행

### 검색 결과 없음
```
관련 정보를 찾을 수 없습니다
```
→ 질문을 더 구체적으로 작성 또는 키워드 변경

## 📁 프로젝트 구조

```
chat_manual/
├── app.py                      # Streamlit 메인 앱
├── config.yaml                 # 설정 파일
├── requirements.txt            # 패키지 의존성
├── .env.example               # 환경변수 예시
├── .gitignore                 # Git 제외 파일
├── README.md                  # 프로젝트 문서
├── PLAN.md                    # 개발 계획
├── PROCEED.md                 # 실행 가이드
├── 2025 학교 업무매뉴얼 행정(최종).pdf
├── .streamlit/
│   ├── config.toml           # Streamlit 설정
│   └── secrets.toml          # API 키 (Git 제외)
├── data/
│   ├── chroma_db/            # ChromaDB 벡터 저장소
│   └── bm25_index.pkl        # BM25 인덱스
├── scripts/
│   ├── analyze_pdf.py        # PDF 구조 분석
│   └── create_database.py    # DB 생성
└── src/
    ├── __init__.py
    ├── pdf_processor.py      # PDF 파싱 및 청킹
    ├── vectorstore.py        # 벡터 DB 관리
    ├── rag_chain.py          # RAG 파이프라인
    └── response_formatter.py  # 응답 포맷팅
```

## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 👥 개발자

- **개발**: deoksangcho
- **모델**: OpenAI GPT-4o mini
- **프레임워크**: Streamlit, LangChain

## 📞 문의

문제가 발생하거나 개선 제안이 있으시면 GitHub Issues를 이용해 주세요.

---

**배포 URL**: https://your-app-name.streamlit.app (배포 후 업데이트)
