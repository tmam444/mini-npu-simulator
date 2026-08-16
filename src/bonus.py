from __future__ import annotations
import time
from custom_types import Matrix, REPEAT_COUNT
from core import mac_operation
from utils import print_section_header

# ==========================================
# 보너스 과제 1: 1차원 배열 변환 최적화
# ==========================================
def flatten_matrix(matrix: Matrix) -> list[float]:
    """2차원 배열을 1차원 배열로 변환합니다."""
    return [val for row in matrix for val in row]

def mac_operation_1d(pattern_1d: list[float], filter_1d: list[float]) -> float:
    """1차원 배열을 이용한 MAC 연산 (메모리 접근 단순화)"""
    score: float = 0.0
    for i in range(len(pattern_1d)):
        score += pattern_1d[i] * filter_1d[i]
    return score

def compare_mac_performance(n: int) -> None:
    """[보너스 1] 2D 배열 vs 1D 배열 MAC 연산 성능 비교"""
    print_section_header(1, f"보너스 1: 성능 비교 (크기 {n}x{n}, 반복 {REPEAT_COUNT}회)")
    
    # 더미 데이터 생성
    pattern_2d = generate_cross_pattern(n)
    filter_2d = generate_cross_pattern(n)
    pattern_1d = flatten_matrix(pattern_2d)
    filter_1d = flatten_matrix(filter_2d)

    # 2D 측정
    start_2d = time.perf_counter()
    for _ in range(REPEAT_COUNT):
        mac_operation(pattern_2d, filter_2d)
    time_2d = (time.perf_counter() - start_2d) * 1000

    # 1D 측정
    start_1d = time.perf_counter()
    for _ in range(REPEAT_COUNT):
        mac_operation_1d(pattern_1d, filter_1d)
    time_1d = (time.perf_counter() - start_1d) * 1000

    print(f"- 2D 배열 MAC 연산 총 소요 시간: {time_2d:.4f} ms")
    print(f"- 1D 배열 MAC 연산 총 소요 시간: {time_1d:.4f} ms")
    if time_1d < time_2d:
        print(f"👉 결론: 1차원 최적화로 약 {time_2d/time_1d:.1f}배 속도 향상!")
    else:
        print(f"👉 결론: 현재 크기에서는 유의미한 차이가 없거나 2D가 빠를 수 있습니다.")

# ==========================================
# 보너스 과제 2: 패턴 자동 생성기
# ==========================================
def generate_cross_pattern(n: int) -> Matrix:
    """N x N 크기의 Cross(+) 패턴 생성"""
    matrix = [[0.0] * n for _ in range(n)]
    mid = n // 2
    for i in range(n):
        matrix[mid][i] = 1.0
        matrix[i][mid] = 1.0
    return matrix

def generate_x_pattern(n: int) -> Matrix:
    """N x N 크기의 X 패턴 생성"""
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 1.0
        matrix[i][n - 1 - i] = 1.0
    return matrix

def print_matrix(matrix: Matrix) -> None:
    for row in matrix:
        print(" ".join(f"{int(val)}" if val.is_integer() else f"{val:.1f}" for val in row))

def demo_pattern_generator() -> None:
    """[보너스 2] 패턴 생성기 데모"""
    while True:
        try:
            n = int(input("\n패턴 크기 N을 입력하세요 (홀수 권장, 종료: 0): "))
            if n == 0:
                break
            if n < 3:
                print("크기는 3 이상이어야 합니다.")
                continue
            
            print_section_header(2, f"자동 생성된 {n}x{n} Cross(+) 패턴")
            print_matrix(generate_cross_pattern(n))
            
            print_section_header(3, f"자동 생성된 {n}x{n} X 패턴")
            print_matrix(generate_x_pattern(n))
            
        except ValueError:
            print("올바른 정수를 입력하세요.")
