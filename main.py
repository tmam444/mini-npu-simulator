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

def input_3x3_matrix(prompt_title: str) -> list:
    """3x3 행렬을 공백 기준으로 입력받고 검증합니다."""
    print(f"\n{prompt_title} (3줄 입력, 공백 구분)")
    while True:
        matrix = []
        try:
            for _ in range(3):
                line = input().strip()
                row = [float(x) for x in line.split()]
                if len(row) != 3:
                    raise ValueError
                matrix.append(row)
            return matrix
        except ValueError:
            print("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요. 다시 입력해주세요:")
            # 버퍼에 남은 입력들을 지우는 효과를 위해 예외 발생 시 다시 입력을 받습니다.
            pass

def mode1_user_input():
    print("\n#----------------------------------------")
    print("# [1] 필터 입력")
    print("#---------------------------------------")
    filter_a = input_3x3_matrix("필터 A")
    filter_b = input_3x3_matrix("필터 B")
    
    print("\n#---------------------------------------")
    print("# [2] 패턴 입력")
    print("#---------------------------------------")
    pattern = input_3x3_matrix("패턴")
    
    print("\n#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")
    
    # 시간 측정 및 연산 (A)
    start_time = time.perf_counter()
    score_a = 0.0
    for _ in range(10):  # 10회 반복 측정
        score_a = mac_operation(pattern, filter_a)
    avg_time_a = (time.perf_counter() - start_time) / 10 * 1000

    # 시간 측정 및 연산 (B)
    start_time = time.perf_counter()
    score_b = 0.0
    for _ in range(10):
        score_b = mac_operation(pattern, filter_b)
    avg_time_b = (time.perf_counter() - start_time) / 10 * 1000
    
    avg_time_total = (avg_time_a + avg_time_b) / 2
    
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_time_total:.3f} ms")
    
    if abs(score_a - score_b) < 1e-9:
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    elif score_a > score_b:
        print("판정: A")
    else:
        print("판정: B")

def main():
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    choice = input("선택: ").strip()
    
    if choice == "1":
        mode1_user_input()
    elif choice == "2":
        print("data.json 분석 모드는 다음 단계에서 개발될 예정입니다.")
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()
