from __future__ import annotations
import json

def load_json_data(filepath: str) -> dict | None:
    """JSON 파일을 읽어 dict로 반환합니다. 실패 시 None을 반환합니다."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        return data
    except Exception as e:
        print(f"JSON 파일을 읽을 수 없습니다: {e}")
        return None

def print_section_header(number: int, title: str) -> None:
    """콘솔에 섹션 구분 헤더를 출력합니다."""
    print(f"\n#---------------------------------------")
    print(f"# [{number}] {title}")
    print(f"#---------------------------------------")
