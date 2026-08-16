from __future__ import annotations
from custom_types import Matrix, MODE1_SIZE, EPSILON
from core import measure_mac_time
from utils import print_section_header

def input_nxn_matrix(prompt_title: str, size: int = MODE1_SIZE) -> Matrix:
    """NxN 행렬을 콘솔에서 공백 기준으로 입력받고 검증합니다."""
    print(f"\n{prompt_title} ({size}줄 입력, 공백 구분)")
    while True:
        matrix: Matrix = []
        try:
            for _ in range(size):
                line: str = input().strip()
                row: list[float] = [float(x) for x in line.split()]
                if len(row) != size:
                    raise ValueError
                matrix.append(row)
            return matrix
        except ValueError:
            print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요. 다시 입력해주세요:")

def print_mode1_result(score_a: float, score_b: float, avg_time_ms: float) -> None:
    """모드 1의 MAC 연산 결과(점수, 시간, 판정)를 출력합니다."""
    print(f"A 점수: {score_a} (값이 높을수록 필터 A와 유사함)")
    print(f"B 점수: {score_b} (값이 높을수록 필터 B와 유사함)")
    print(f"연산 시간(평균/10회): {avg_time_ms:.3f} ms")
    if abs(score_a - score_b) < EPSILON:
        print("판정: 판정 불가")
    elif score_a > score_b:
        print("판정: A")
    else:
        print("판정: B")

def mode1_user_input() -> None:
    """[모드 1] 사용자가 3×3 필터 2개(A, B)와 패턴을 직접 입력합니다."""
    print_section_header(1, "필터 입력")
    filter_a: Matrix = input_nxn_matrix("필터 A")
    filter_b: Matrix = input_nxn_matrix("필터 B")

    print_section_header(2, "패턴 입력")
    pattern: Matrix = input_nxn_matrix("패턴")

    print_section_header(3, "MAC 결과")
    score_a: float; time_a: float
    score_a, time_a = measure_mac_time(pattern, filter_a)
    score_b: float; time_b: float
    score_b, time_b = measure_mac_time(pattern, filter_b)
    
    avg_time: float = (time_a + time_b) / 2
    print_mode1_result(score_a, score_b, avg_time)
