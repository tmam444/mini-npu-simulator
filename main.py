import sys
import json
import time

def normalize_label(label: str) -> str:
    """
    입력된 라벨을 'Cross' 또는 'X' 표준 라벨로 정규화합니다.
    (예: '+', 'cross' -> 'Cross' / 'x', 'X' -> 'X')
    """
    l = label.strip().lower()
    if l in ['+', 'cross']:
        return 'Cross'
    if l in ['x']:
        return 'X'
    return 'UNKNOWN'

def mac_operation(pattern: list, filter_matrix: list) -> float:
    """
    입력 패턴과 필터 배열의 MAC(Multiply-Accumulate) 연산을 수행합니다.
    외부 라이브러리 없이 반복문으로 직접 구현합니다.
    """
    score = 0.0
    n = len(pattern)
    for r in range(n):
        for c in range(n):
            score += pattern[r][c] * filter_matrix[r][c]
    return score

def decide_result(score_cross: float, score_x: float, epsilon: float = 1e-9) -> str:
    """
    부동소수점 오차를 고려한 허용오차(epsilon) 기반 비교 정책을 적용하여 
    최종 판정(Cross / X / UNDECIDED)을 내립니다.
    """
    if abs(score_cross - score_x) < epsilon:
        return 'UNDECIDED'
    if score_cross > score_x:
        return 'Cross'
    return 'X'

def main():
    print("=== Mini NPU Simulator ===")
    print("핵심 코어 모듈(MAC 연산 및 판정 함수)이 준비되었습니다.\n")
    # 향후 모드 1(사용자 입력) 및 모드 2(json 분석) 로직이 여기에 추가됩니다.

if __name__ == "__main__":
    main()
