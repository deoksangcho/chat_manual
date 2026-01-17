"""
학교 행정매뉴얼 RAG 챗봇 - Streamlit 앱
"""

import streamlit as st
import os
import yaml
from dotenv import load_dotenv

from src.vectorstore import load_vectorstore, load_bm25_index, check_database_exists
from src.rag_chain import process_query
from src.response_formatter import validate_response_structure, format_response


# 페이지 설정
st.set_page_config(
    page_title="학교 행정매뉴얼 챗봇",
    page_icon="🏫",
    layout="wide"
)


def load_config():
    """config.yaml 로드"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def init_session_state():
    """세션 스테이트 초기화"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    
    if 'bm25' not in st.session_state:
        st.session_state.bm25 = None
    
    if 'bm25_chunks' not in st.session_state:
        st.session_state.bm25_chunks = None
    
    if 'config' not in st.session_state:
        st.session_state.config = None


def load_databases():
    """데이터베이스 로드"""
    if st.session_state.vectorstore is None:
        config = load_config()
        st.session_state.config = config
        
        # DB 존재 확인
        if not check_database_exists(
            config['database']['chroma_path'],
            config['database']['bm25_path']
        ):
            st.error("❌ 데이터베이스를 찾을 수 없습니다. `python scripts/create_database.py`를 먼저 실행해 주세요.")
            st.stop()
        
        with st.spinner("데이터베이스 로드 중..."):
            # ChromaDB 로드
            st.session_state.vectorstore = load_vectorstore(config)
            
            # BM25 로드
            st.session_state.bm25, st.session_state.bm25_chunks = load_bm25_index(
                config['database']['bm25_path']
            )


def main():
    # 세션 초기화
    init_session_state()
    
    # 제목
    st.title("🏫 학교 행정매뉴얼 챗봇")
    st.markdown("**2025 학교 업무매뉴얼 행정** 기반 질의응답 시스템")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # API 키 설정: Streamlit Cloud에서는 Secrets 사용, 로컬에서는 .env 사용
        api_key = None
        try:
            # 배포 환경: Secrets에서 자동 로드 (사용자에게 보이지 않음)
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
                st.success("✅ API 키가 안전하게 로드되었습니다")
        except (FileNotFoundError, AttributeError):
            # 로컬 환경: .env에서 로드하거나 사용자 입력
            load_dotenv()
            default_key = os.getenv("OPENAI_API_KEY", "")
            api_key = st.text_input(
                "OpenAI API 키",
                type="password",
                value=default_key,
                help="로컬 테스트용. 배포 시에는 Streamlit Secrets 사용"
            )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        st.divider()
        
        # 정보
        st.markdown("### 📊 시스템 정보")
        st.info("""
        - **모델**: GPT-4o mini
        - **임베딩**: text-embedding-3-small
        - **검색**: Hybrid (Vector + BM25)
        """)
        
        st.divider()
        
        # 사용 가이드
        with st.expander("📖 사용 가이드"):
            st.markdown("""
            **질문 예시:**
            - 공문서 접수 절차는 어떻게 되나요?
            - 예산 집행 시 주의사항은?
            - 근무성적평정 관련 법령은?
            
            **답변 구조:**
            1. 질문 요지 정리
            2. 절차
            3. 관련 법령
            4. 서식
            5. 주의사항
            6. 출처
            """)
        
        st.divider()
        
        # 대화 초기화
        if st.button("🗑️ 대화 내역 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ OpenAI API 키를 입력해 주세요 (사이드바)")
        st.stop()
    
    # 데이터베이스 로드
    load_databases()
    
    # 대화 내역 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("학교 행정 업무에 대해 질문해 주세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                try:
                    response = process_query(
                        query=prompt,
                        vectorstore=st.session_state.vectorstore,
                        bm25=st.session_state.bm25,
                        bm25_chunks=st.session_state.bm25_chunks,
                        config=st.session_state.config
                    )
                    
                    # 응답 표시
                    st.markdown(response)
                    
                    # 구조 검증 (선택적)
                    validation = validate_response_structure(response)
                    missing = [k for k, v in validation.items() if not v]
                    
                    if missing:
                        with st.expander("⚠️ 답변 구조 확인"):
                            st.warning(f"누락된 섹션: {', '.join(missing)}")
                    
                    # 메시지 저장
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    error_msg = f"❌ 오류가 발생했습니다: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # 푸터
    st.divider()
    st.caption("💡 학교 행정 업무매뉴얼 기반 RAG 챗봇 | 정확한 답변을 위해 문서 내용만 참조합니다")


if __name__ == "__main__":
    main()
