"""
답변 포맷터 모듈
- 답변 구조 검증
- 필수 섹션 확인
"""

import re
from typing import Dict, List


def validate_response_structure(response: str) -> Dict[str, bool]:
    """
    답변 구조 검증
    
    Args:
        response: LLM 답변
        
    Returns:
        검증 결과 딕셔너리
    """
    required_sections = [
        r'###\s*①\s*질문\s*요지\s*정리',
        r'###\s*②\s*절차',
        r'###\s*③\s*관련\s*법령',
        r'###\s*④\s*서식',
        r'###\s*⑤\s*주의사항',
        r'###\s*📄\s*출처'
    ]
    
    validation = {}
    
    for i, pattern in enumerate(required_sections, start=1):
        section_name = ['질문 요지 정리', '절차', '관련 법령', '서식', '주의사항', '출처'][i-1]
        validation[section_name] = bool(re.search(pattern, response))
    
    return validation


def format_response(response: str) -> str:
    """
    답변 포맷팅 (필요시 후처리)
    
    Args:
        response: LLM 답변
        
    Returns:
        포맷팅된 답변
    """
    # 현재는 그대로 반환, 필요시 추가 포맷팅 가능
    return response


def extract_sections(response: str) -> Dict[str, str]:
    """
    답변에서 각 섹션 추출
    
    Args:
        response: LLM 답변
        
    Returns:
        섹션별 내용 딕셔너리
    """
    sections = {
        '질문 요지 정리': '',
        '절차': '',
        '관련 법령': '',
        '서식': '',
        '주의사항': '',
        '출처': ''
    }
    
    # 각 섹션을 정규식으로 추출
    patterns = {
        '질문 요지 정리': r'###\s*①\s*질문\s*요지\s*정리\s*\n(.*?)(?=###|$)',
        '절차': r'###\s*②\s*절차\s*\n(.*?)(?=###|$)',
        '관련 법령': r'###\s*③\s*관련\s*법령\s*\n(.*?)(?=###|$)',
        '서식': r'###\s*④\s*서식\s*\n(.*?)(?=###|$)',
        '주의사항': r'###\s*⑤\s*주의사항\s*\n(.*?)(?=###|$)',
        '출처': r'###\s*📄\s*출처\s*\n(.*?)(?=###|$)'
    }
    
    for section_name, pattern in patterns.items():
        match = re.search(pattern, response, re.DOTALL)
        if match:
            sections[section_name] = match.group(1).strip()
    
    return sections


def get_missing_sections(validation: Dict[str, bool]) -> List[str]:
    """
    누락된 섹션 목록 반환
    
    Args:
        validation: 검증 결과
        
    Returns:
        누락된 섹션 목록
    """
    return [section for section, exists in validation.items() if not exists]
