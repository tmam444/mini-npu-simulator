from __future__ import annotations
"""
Mini NPU Simulator - main.py

MAC(Multiply-Accumulate) 연산을 통해 입력 패턴이 Cross인지 X인지 판별하는
NPU 시뮬레이터입니다. 외부 라이브러리 없이 반복문으로 직접 구현합니다.
"""

import sys
from mode1 import mode1_user_input
from mode2 import mode2_json_analysis

def main() -> None:
    """
    프로그램 진입점. 모드(1: 사용자 입력 / 2: JSON 분석)를 선택합니다.
    """
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 및 자동 생성 (보너스 연동)")
    print("2. data.json 분석")
    choice: str = input("선택: ").strip()

    if choice == "1":
        mode1_user_input()
    elif choice == "2":
        mode2_json_analysis()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    sys.exit(main())
