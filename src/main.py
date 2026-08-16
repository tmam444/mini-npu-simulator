from __future__ import annotations
"""
Mini NPU Simulator - main.py

MAC(Multiply-Accumulate) 연산을 통해 입력 패턴이 Cross인지 X인지 판별하는
NPU 시뮬레이터입니다. 외부 라이브러리 없이 반복문으로 직접 구현합니다.
"""

import sys
from mode1 import mode1_user_input
from mode2 import mode2_json_analysis
from bonus import compare_mac_performance, demo_pattern_generator

def main() -> None:
    """
    프로그램 진입점. 모드(1: 사용자 입력 / 2: JSON 분석 / 3: 보너스 1 / 4: 보너스 2)를 선택합니다.
    """
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("3. [보너스 1] 1차원 배열 최적화 성능 비교")
    print("4. [보너스 2] 패턴 생성기 테스트")
    choice: str = input("선택: ").strip()

    if choice == "1":
        mode1_user_input()
    elif choice == "2":
        mode2_json_analysis()
    elif choice == "3":
        try:
            n = int(input("테스트할 행렬 크기 N을 입력하세요 (예: 100): "))
            compare_mac_performance(n)
        except ValueError:
            print("올바른 숫자를 입력하세요.")
    elif choice == "4":
        demo_pattern_generator()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    sys.exit(main())
