"""
PDF 구조 분석 도구
- PDF 기본 정보 추출
- 문서 구조 분석
- 청킹 전략 제안
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # PyMuPDF
import re
from collections import Counter


def analyze_pdf_structure(pdf_path: str):
    """
    PDF 구조 상세 분석
    
    Args:
        pdf_path: PDF 파일 경로
    """
    try:
        doc = fitz.open(pdf_path)
    except FileNotFoundError:
        print(f"❌ 오류: PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return
    
    print("=" * 80)
    print("PDF 구조 분석 보고서")
    print("=" * 80)
    print()
    
    # 1. 기본 정보
    print("📌 1. PDF 기본 정보")
    print("-" * 80)
    print(f"파일명: {os.path.basename(pdf_path)}")
    print(f"총 페이지 수: {len(doc)} 페이지")
    print(f"파일 크기: {os.path.getsize(pdf_path):,} bytes ({os.path.getsize(pdf_path)/1024/1024:.2f} MB)")
    print(f"텍스트 추출 가능 여부: 가능" if doc[0].get_text() else "불가능")
    print()
    
    # 2. 문서 구조 분석
    print("📌 2. 문서 구조 분석")
    print("-" * 80)
    
    # 모든 텍스트 추출
    all_text = ""
    char_counts = []
    
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        all_text += text
        char_counts.append(len(text))
    
    # 제목 패턴 분석
    print("[목차 샘플 - 처음 20개 항목]:")
    
    # 로마숫자 패턴
    roman_pattern = r'^([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)\.\s*(.+)$'
    roman_matches = re.findall(roman_pattern, all_text, re.MULTILINE)
    
    # 숫자 패턴
    number_pattern = r'^(\d+)\.\s+([가-힣].+)$'
    number_matches = re.findall(number_pattern, all_text, re.MULTILINE)
    
    # 하이픈 패턴
    hyphen_pattern = r'^(\d+-\d+)\s+(.+)$'
    hyphen_matches = re.findall(hyphen_pattern, all_text, re.MULTILINE)
    
    count = 0
    for match in roman_matches[:5]:
        print(f"  [Level 1] {match[0]}. {match[1]}")
        count += 1
        if count >= 20:
            break
    
    for match in number_matches[:10]:
        print(f"    [Level 2] {match[0]}. {match[1]}")
        count += 1
        if count >= 20:
            break
    
    for match in hyphen_matches[:10]:
        print(f"      [Level 3] {match[0]} {match[1]}")
        count += 1
        if count >= 20:
            break
    
    print()
    print(f"발견된 제목 수:")
    print(f"  - 대분류 (로마숫자): {len(roman_matches)}개")
    print(f"  - 중분류 (숫자): {len(number_matches)}개")
    print(f"  - 소분류 (하이픈): {len(hyphen_matches)}개")
    print()
    
    # 3. 텍스트 밀도
    print("📌 3. 텍스트 밀도 분석")
    print("-" * 80)
    avg_chars = sum(char_counts) / len(char_counts)
    print(f"페이지당 평균 문자 수: {avg_chars:.0f}자")
    print(f"최소 문자 수: {min(char_counts)}자 (페이지 {char_counts.index(min(char_counts)) + 1})")
    print(f"최대 문자 수: {max(char_counts)}자 (페이지 {char_counts.index(max(char_counts)) + 1})")
    print()
    
    # 4. 특수 요소 탐지
    print("📌 4. 특수 요소 탐지")
    print("-" * 80)
    
    # 법령 패턴
    law_patterns = [
        (r'제\s*\d+조', '법 조항'),
        (r'[가-힣]+법\s*제', '법명'),
        (r'시행령', '시행령'),
        (r'시행규칙', '시행규칙')
    ]
    
    for pattern, name in law_patterns:
        matches = re.findall(pattern, all_text)
        print(f"  - {name}: {len(matches)}회 등장")
    
    # 서식 패턴
    form_patterns = [
        (r'서식\s*\d+', '서식 번호'),
        (r'<서식[^>]*>', '서식 태그1'),
        (r'【서식[^】]*】', '서식 태그2')
    ]
    
    for pattern, name in form_patterns:
        matches = re.findall(pattern, all_text)
        print(f"  - {name}: {len(matches)}회 등장")
    
    print()
    
    # 5. 청킹 전략 제안
    print("📌 5. 청킹 전략 제안")
    print("-" * 80)
    print(f"권장 청크 크기: 1000-1500자 (평균 페이지 크기의 약 {1200/avg_chars:.1f}배)")
    print(f"권장 오버랩: 150-200자")
    print()
    print("권장 구분자 우선순위:")
    print("  1. \\n\\n\\n (대분류 구분)")
    print("  2. \\n\\n (중분류 구분)")
    print("  3. \\n (소분류/문단)")
    print("  4. . (문장)")
    print("  5. (공백)")
    print()
    
    print("=" * 80)
    print("✅ 분석 완료!")
    print("=" * 80)
    
    doc.close()


if __name__ == "__main__":
    # PDF 파일 경로
    pdf_path = "2025 학교 업무매뉴얼 행정(최종).pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ 오류: PDF 파일을 찾을 수 없습니다: {pdf_path}")
        print(f"현재 디렉토리: {os.getcwd()}")
        print(f"파일 목록: {os.listdir('.')}")
        sys.exit(1)
    
    analyze_pdf_structure(pdf_path)
