# 학교 행정매뉴얼 RAG 챗봇 - 실행 가이드

## 🚀 빠른 시작 (Quick Start)

### 전제 조건
- Python 3.10 이상
- OpenAI API 키 (GPT-4o mini, text-embedding-3-small 사용 가능)
- Git

---

## 📋 단계별 실행 절차

### Phase 1: 환경 설정 (5분)

#### 1-1. 저장소 준비
```bash
cd /Users/cds/chatbot
```

#### 1-2. 가상환경 생성
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate
```

#### 1-3. 의존성 설치
```bash
# requirements.txt 설치
pip install -r requirements.txt
```

#### 1-4. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

`.env` 파일 내용:
```bash
# OpenAI API 키 입력
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx

# 관리자 비밀번호 설정 (12자 이상, 영문+숫자+특수문자)
ADMIN_PASSWORD=Adm1n!2025@School#
```

---

### Phase 2: PDF 구조 분석 (10분)

#### 2-1. 분석 스크립트 실행
```bash
python scripts/analyze_pdf.py
```

**출력 예시**:
```
================================================================================
PDF 구조 분석 보고서
================================================================================

📌 1. PDF 기본 정보
--------------------------------------------------------------------------------
파일명: 2025 학교 업무매뉴얼 행정(최종).pdf
총 페이지 수: 245 페이지
파일 크기: 8,542,156 bytes (8.15 MB)
텍스트 추출 가능 여부: 가능

📌 2. 문서 구조 분석
--------------------------------------------------------------------------------
[목차 샘플 - 처음 20개 항목]:
  [Level 1] Ⅰ. 총무 (페이지 5)
    [Level 2] 1. 문서관리 (페이지 7)
      [Level 3] 1-1 공문서 접수 (페이지 8)
...
```

#### 2-2. 분석 결과 확인
- 제목 계층 패턴 확인 (로마숫자, 숫자, 하이픈)
- 페이지당 평균 문자 수 확인
- 법령, 서식 패턴 확인

#### 2-3. config.yaml 조정 (필요 시)
분석 결과를 바탕으로 `config.yaml`의 청킹 설정 미세 조정:
```yaml
chunking:
  chunk_size: 1200    # 필요시 조정
  chunk_overlap: 150  # 필요시 조정
```

---

### Phase 3: 데이터베이스 생성 (3-5분)

#### 3-1. DB 생성 스크립트 실행
```bash
python scripts/create_database.py
```

**실행 화면 예시**:
```
================================================================================
학교 행정매뉴얼 데이터베이스 생성
================================================================================

[1/6] config.yaml 로드 중... ✓
[2/6] PDF 파일 로드 중... ✓
      - 총 245 페이지
[3/6] 텍스트 추출 및 청킹 중...
      100%|████████████████████| 245/245 [00:15<00:00, 16.12 pages/s]
      - 총 187개 청크 생성
[4/6] OpenAI 임베딩 생성 중...
      100%|████████████████████| 187/187 [01:23<00:00,  2.25 chunks/s]
[5/6] ChromaDB 저장 중... ✓
      - 저장 경로: ./data/chroma_db
[6/6] BM25 인덱스 생성 중... ✓
      - 저장 경로: ./data/bm25_index.pkl

================================================================================
✅ 데이터베이스 생성 완료!
================================================================================
총 소요 시간: 2분 43초
임베딩 비용: $0.0042
```

#### 3-2. 생성 확인
```bash
# 생성된 파일 확인
ls -lh data/
```

**출력 예시**:
```
drwxr-xr-x  chroma_db/
-rw-r--r--  bm25_index.pkl (2.3M)
```

---

### Phase 4: 로컬 테스트 (5분)

#### 4-1. Streamlit 앱 실행
```bash
streamlit run app.py
```

**출력 예시**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.0.15:8501
```

#### 4-2. 브라우저 접속
- 자동으로 브라우저가 열림
- 또는 `http://localhost:8501` 수동 접속

#### 4-3. 기본 기능 테스트
1. **API 키 입력** (사이드바)
2. **테스트 질문 입력**:
   - "공문서 접수 절차는 어떻게 되나요?"
   - "예산 집행 시 주의사항은 무엇인가요?"
3. **답변 구조 확인**:
   - ① 질문 요지 정리
   - ② 절차
   - ③ 관련 법령
   - ④ 서식
   - ⑤ 주의사항
   - 📄 출처

#### 4-4. DB 갱신 기능 테스트
1. 사이드바 하단 "🔧 데이터베이스 갱신" 펼치기
2. 관리자 비밀번호 입력
3. 잘못된 비밀번호로 테스트 → 에러 확인
4. 올바른 비밀번호로 테스트 (실제 갱신하지 않음)

---

### Phase 5: 자동 평가 (10분)

#### 5-1. 테스트 질문 실행
```bash
cd tests
python evaluate.py
```

**출력 예시**:
```
================================================================================
질문 1: 공문서 접수 절차는 어떻게 되나요?
================================================================================

### ① 질문 요지 정리
공문서 접수 절차에 대한 단계별 안내를 요청하셨습니다.

### ② 절차
1. 공문서 접수대장에 기록
2. 담당 부서 배정
3. 결재 상신
4. 시행

### ③ 관련 법령
- 공공기록물 관리에 관한 법률 제3조
- 행정 효율과 협업 촉진에 관한 규정 제5조

### ④ 서식
- 서식 1-1: 공문서 접수대장

### ⑤ 주의사항
- 접수 즉시 처리 원칙
- 긴급 공문의 경우 우선 처리

### 📄 출처
- Ⅰ. 총무 > 1. 문서관리 > 1-1 공문서 접수 (8-9페이지)

...

================================================================================
평가 결과 요약
================================================================================
총 질문 수: 15
성공: 15/15 (100.0%)
구조 준수: 15/15 (100.0%)
```

#### 5-2. 결과 분석
- 성공률 90% 이상 → 배포 가능
- 성공률 90% 미만 → `config.yaml` 조정 후 재테스트

---

### Phase 6: GitHub 푸시 (5분)

#### 6-1. Git 초기화 (처음 한 번만)
```bash
# 현재 디렉토리 확인
pwd  # /Users/cds/chatbot

# Git 초기화 (이미 되어있으면 생략)
git init

# 원격 저장소 추가 (GitHub에서 repo 생성 후)
git remote add origin https://github.com/your-username/school-chatbot.git
```

#### 6-2. 파일 추가 및 커밋
```bash
# 전체 파일 추가 (.gitignore에 따라 필터링됨)
git add .

# 커밋
git commit -m "Initial commit: 학교 행정매뉴얼 RAG 챗봇"

# 푸시
git push -u origin main
```

#### 6-3. 푸시 확인
```bash
# GitHub 웹사이트에서 확인
# 다음 파일들이 업로드되었는지 확인:
# - data/chroma_db/ (벡터 DB)
# - data/bm25_index.pkl (BM25 인덱스)
# - 2025 학교 업무매뉴얼 행정(최종).pdf
# - 모든 소스 코드 파일
# - .env는 제외됨 (.gitignore)
```

---

### Phase 7: Streamlit Cloud 배포 (10분)

#### 7-1. Streamlit Cloud 가입 및 로그인
1. [https://streamlit.io/cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인

#### 7-2. 새 앱 배포
1. **"New app"** 버튼 클릭
2. **Repository**: `your-username/school-chatbot` 선택
3. **Branch**: `main`
4. **Main file path**: `app.py`
5. **App URL**: 원하는 URL 설정 (예: `school-admin-chatbot`)

#### 7-3. Advanced settings (선택)
```toml
Python version: 3.10
```

#### 7-4. Secrets 설정 ⚠️ **중요**
**Settings > Secrets** 클릭 후 다음 내용 입력:

```toml
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxx"
ADMIN_PASSWORD = "Adm1n!2025@School#"
```

**주의**: 
- 큰따옴표 사용
- 실제 API 키와 비밀번호로 교체
- 저장 후 앱 재시작

#### 7-5. 배포 시작
**"Deploy!"** 버튼 클릭

#### 7-6. 배포 진행 확인
```
Building... (약 2-3분)
├─ Installing dependencies...
├─ Loading data...
└─ Starting app...

✅ Your app is live!
🌐 https://school-admin-chatbot.streamlit.app
```

#### 7-7. 배포 완료 테스트
1. 제공된 URL 접속
2. 로그인 없이 바로 사용 가능 (API 키는 Secrets에서 자동 로드)
3. 테스트 질문 입력 및 답변 확인
4. DB 갱신 기능 테스트 (관리자 비밀번호 필요)

---

## 🔧 문제 해결

### 문제 1: "ModuleNotFoundError: No module named 'xxx'"
**원인**: 의존성 미설치

**해결**:
```bash
pip install -r requirements.txt
```

---

### 문제 2: "OpenAI API key not found"
**원인**: 환경변수 미설정

**해결** (로컬):
```bash
# .env 파일 확인
cat .env

# API 키가 없으면 추가
echo "OPENAI_API_KEY=sk-proj-xxxxx" >> .env
```

**해결** (Streamlit Cloud):
1. Streamlit Cloud 대시보드 접속
2. 앱 선택 > Settings > Secrets
3. `OPENAI_API_KEY` 추가

---

### 문제 3: "데이터베이스를 찾을 수 없습니다"
**원인**: DB 미생성 또는 경로 오류

**해결**:
```bash
# DB 존재 확인
ls -la data/

# 없으면 생성
python scripts/create_database.py

# GitHub 푸시 (Streamlit Cloud의 경우)
git add data/
git commit -m "Add database"
git push
```

---

### 문제 4: Streamlit Cloud 배포 실패
**원인**: 파일 크기, 의존성 오류 등

**해결**:
1. **로그 확인**: Streamlit Cloud 대시보드에서 에러 로그 확인
2. **파일 크기**: PDF + DB 합계 50MB 이하 확인
3. **의존성**: `requirements.txt` 버전 명시 확인
4. **Secrets**: API 키가 올바르게 설정되었는지 확인

---

### 문제 5: 답변이 부정확하거나 이상함
**원인**: 청킹 설정, 검색 파라미터 부적합

**해결**:
```yaml
# config.yaml 수정

# 검색 결과 수 증가
retrieval:
  final_top_k: 7  # 5 → 7

# 온도 낮춤 (더 보수적)
llm:
  temperature: 0.05  # 0.1 → 0.05
```

재배포:
```bash
git add config.yaml
git commit -m "Update config for better accuracy"
git push
```

---

## 📊 배포 후 체크리스트

### ✅ 기능 테스트
- [ ] 웹앱 접속 가능
- [ ] 질문 입력 및 답변 생성 정상 작동
- [ ] 5단계 답변 구조 정상 출력
- [ ] 출처 정보 표시 정상
- [ ] 대화 초기화 버튼 작동
- [ ] DB 갱신 기능 (관리자 비밀번호 검증)

### ✅ 성능 테스트
- [ ] 답변 생성 시간 5-10초 이내
- [ ] 동시 사용자 2-3명 테스트
- [ ] API 비용 모니터링 설정

### ✅ 보안 체크
- [ ] `.env` 파일이 GitHub에 푸시되지 않음
- [ ] Streamlit Secrets에 API 키 안전하게 저장
- [ ] 관리자 비밀번호 강도 충분 (12자 이상)

### ✅ 문서화
- [ ] README.md 작성 완료
- [ ] PLAN.md 업데이트
- [ ] 사용자 가이드 전달 (필요시)

---

## 🔄 연간 유지보수 절차

### 매년 1월: DB 갱신

#### 1. 새 PDF 준비
```bash
# 새 PDF를 프로젝트 폴더에 복사
cp ~/Downloads/2026\ 학교\ 업무매뉴얼\ 행정\(최종\).pdf .
```

#### 2. 웹앱에서 갱신
1. Streamlit 앱 접속
2. 사이드바 하단 "🔧 데이터베이스 갱신" 펼치기
3. 관리자 비밀번호 입력
4. 새 PDF 업로드
5. "🔄 데이터베이스 갱신" 버튼 클릭
6. 진행률 확인 (3-5분)
7. "✅ 데이터베이스가 갱신되었습니다!" 메시지 확인

#### 3. 검증
```bash
# 테스트 질문 실행
cd tests
python evaluate.py
```

#### 4. GitHub 백업 (선택)
```bash
# 새 DB를 GitHub에 백업
git add data/
git commit -m "Update database for 2026"
git push
```

---

## 📈 모니터링

### OpenAI 사용량 확인
1. [OpenAI Platform](https://platform.openai.com/usage) 접속
2. Usage 탭에서 일일/월간 비용 확인
3. 예상 비용: 월 $0.10 이하

### Streamlit Cloud 상태 확인
1. [Streamlit Cloud Dashboard](https://share.streamlit.io/) 접속
2. 앱 상태 (Running/Stopped) 확인
3. 로그 확인 (에러 발생 시)

---

## 🎯 다음 단계 (선택 사항)

### 개선 옵션
1. **Cross-Encoder 재순위화**: 검색 정확도 10-15% 향상
2. **대화 컨텍스트 유지**: "그럼 서식은 뭐가 필요해?" 같은 후속 질문 지원
3. **질문 빈도 분석**: 자주 묻는 질문 대시보드
4. **다중 매뉴얼 지원**: 교무, 학생, 재무 매뉴얼 통합

### 사용자 교육
- 2-3명의 사용자에게 웹앱 URL 전달
- 간단한 사용 가이드 제공 (README.md 기반)
- 피드백 수집 채널 마련 (이메일, Slack 등)

---

## 📞 지원

### 문제 발생 시
1. **에러 로그 확인**: Streamlit Cloud 대시보드
2. **API 상태 확인**: [OpenAI Status](https://status.openai.com/)
3. **GitHub Issues**: 프로젝트 저장소에서 이슈 생성

---

**🎉 축하합니다! 학교 행정매뉴얼 RAG 챗봇이 성공적으로 배포되었습니다.**
