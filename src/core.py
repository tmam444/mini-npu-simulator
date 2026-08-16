from __future__ import annotations
import time
from custom_types import Matrix, EPSILON, REPEAT_COUNT

def normalize_label(label: str) -> str:
    """
    다양한 형태의 라벨 입력을 표준 라벨('Cross' 또는 'X')로 정규화합니다.
    """
    normalized: str = label.strip().lower()
    if normalized in ['+', 'cross']:
        return 'Cross'
    if normalized in ['x']:
        return 'X'
    return 'UNKNOWN'

def mac_operation(pattern: Matrix, filter_matrix: Matrix) -> float:
    """
    두 NxN 행렬의 MAC(Multiply-Accumulate) 연산을 수행합니다.
    """
    score: float = 0.0
    n: int = len(pattern)
    for r in range(n):
        for c in range(n):
            score += pattern[r][c] * filter_matrix[r][c]
    return score

def decide_result(score_cross: float, score_x: float, epsilon: float = EPSILON) -> str:
    """
    부동소수점 허용오차(epsilon) 기반으로 최종 판정을 내립니다.
    """
    if abs(score_cross - score_x) < epsilon:
        return 'UNDECIDED'
    if score_cross > score_x:
        return 'Cross'
    return 'X'

def measure_mac_time(
    pattern: Matrix, filter_matrix: Matrix, repeats: int = REPEAT_COUNT
) -> tuple[float, float]:
    """
    MAC 연산을 repeats회 반복 실행하여 (최종 점수, 평균 시간 ms)를 반환합니다.
    """
    start: float = time.perf_counter()
    score: float = 0.0
    for _ in range(repeats):
        score = mac_operation(pattern, filter_matrix)
    elapsed_ms: float = (time.perf_counter() - start) / repeats * 1000
    return score, elapsed_ms
