"""
Mini NPU Simulator - main.py

MAC(Multiply-Accumulate) 연산을 통해 입력 패턴이 Cross인지 X인지 판별하는
NPU 시뮬레이터입니다. 외부 라이브러리 없이 반복문으로 직접 구현합니다.

[모드 1] 사용자가 3×3 필터 2개와 패턴을 직접 입력하여 판정
[모드 2] data.json에서 다양한 크기(5×5, 13×13, 25×25)의 필터/패턴을 로드하여
         일괄 판정 및 성능 분석 수행
"""

from __future__ import annotations

import sys
import json
import time
from typing import Dict, List, Optional, Tuple, Union

# ──────────────────────────────────────────────
# 타입 별칭 정의
#   - Matrix: 2차원 float 리스트 (NxN 행렬)
#   - PerfDict: 성능 데이터를 축적하는 딕셔너리
# ──────────────────────────────────────────────
Matrix = List[List[float]]
PerfDict = Dict[str, Dict[str, Union[float, int]]]

# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────
EPSILON: float = 1e-9          # 부동소수점 비교 허용오차
REPEAT_COUNT: int = 10         # 성능 측정 반복 횟수
MODE1_SIZE: int = 3            # 모드 1 행렬 크기 고정값


# ================================================================
# 1. 라벨 정규화 (Label Normalization)
# ================================================================

def normalize_label(label: str) -> str:
    """
    다양한 형태의 라벨 입력을 표준 라벨('Cross' 또는 'X')로 정규화합니다.

    [정규화 규칙]
      '+', 'cross' → 'Cross'
      'x'          → 'X'
      그 외         → 'UNKNOWN'

    [분리 이유]
      data.json의 expected 값('+', 'x')과 filter 키('cross', 'x')가 서로
      다른 형식을 사용하므로, 비교 전에 반드시 통일된 라벨로 변환해야 합니다.
      이 함수를 별도로 분리하면 새 라벨('o' 등) 추가 시 이 함수만 수정하면 됩니다.
    """
    normalized: str = label.strip().lower()
    if normalized in ['+', 'cross']:
        return 'Cross'
    if normalized in ['x']:
        return 'X'
    return 'UNKNOWN'


# ================================================================
# 2. MAC 연산 (Multiply-Accumulate Operation)
# ================================================================

def mac_operation(pattern: Matrix, filter_matrix: Matrix) -> float:
    """
    두 NxN 행렬의 MAC(Multiply-Accumulate) 연산을 수행합니다.

    [연산 원리]
      같은 위치의 값을 곱하고(Multiply), 모든 결과를 누적 합산(Accumulate)합니다.
      점수가 높을수록 패턴과 필터가 더 유사하다는 의미입니다.

    [시간 복잡도]
      O(N²) - N×N 행렬의 모든 원소를 한 번씩 순회하므로 연산 횟수는 N²입니다.
      N이 커질수록 연산량이 기하급수적으로 증가하여 NPU 같은 병렬 처리 칩이 필요합니다.
    """
    score: float = 0.0
    n: int = len(pattern)
    for r in range(n):
        for c in range(n):
            score += pattern[r][c] * filter_matrix[r][c]
    return score


# ================================================================
# 3. 판정 로직 (Decision Logic)
# ================================================================

def decide_result(score_cross: float, score_x: float, epsilon: float = EPSILON) -> str:
    """
    부동소수점 허용오차(epsilon) 기반으로 최종 판정을 내립니다.

    [부동소수점 오차란?]
      컴퓨터는 실수를 2진수로 근사 표현하므로 0.1+0.2 ≠ 0.3 같은 미세 오차가
      발생합니다. 따라서 == 대신 abs(a-b) < epsilon 방식으로 비교해야 합니다.

    [반환값]
      'Cross'     : Cross 점수가 더 높을 때
      'X'         : X 점수가 더 높을 때
      'UNDECIDED' : 두 점수 차이가 epsilon 미만(동점)일 때
    """
    if abs(score_cross - score_x) < epsilon:
        return 'UNDECIDED'
    if score_cross > score_x:
        return 'Cross'
    return 'X'


# ================================================================
# 4. 시간 측정 유틸리티
# ================================================================

def measure_mac_time(
    pattern: Matrix, filter_matrix: Matrix, repeats: int = REPEAT_COUNT
) -> tuple[float, float]:
    """
    MAC 연산을 repeats회 반복 실행하여 (최종 점수, 평균 시간 ms)를 반환합니다.

    [측정 경계]
      time.perf_counter()로 연산 함수 호출 구간만 감싸서 측정합니다.
      I/O(출력, 파일 읽기)는 측정 범위에서 제외됩니다.
    """
    start: float = time.perf_counter()
    score: float = 0.0
    for _ in range(repeats):
        score = mac_operation(pattern, filter_matrix)
    elapsed_ms: float = (time.perf_counter() - start) / repeats * 1000
    return score, elapsed_ms


# ================================================================
# 5. 모드 1 - 사용자 입력 (3×3)
# ================================================================

def input_nxn_matrix(prompt_title: str, size: int = MODE1_SIZE) -> Matrix:
    """
    NxN 행렬을 콘솔에서 공백 기준으로 입력받고 검증합니다.

    [입력 검증]
      - 각 줄의 숫자 개수가 size와 다르면 ValueError 발생 → 재입력 유도
      - float 변환 실패(숫자 아닌 값) 시에도 재입력 유도
      - 프로그램이 종료되지 않고 올바른 입력이 들어올 때까지 반복합니다.
    """
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


def print_section_header(number: int, title: str) -> None:
    """콘솔에 섹션 구분 헤더를 출력합니다."""
    print(f"\n#---------------------------------------")
    print(f"# [{number}] {title}")
    print(f"#---------------------------------------")


def print_mode1_result(
    score_a: float, score_b: float, avg_time_ms: float
) -> None:
    """
    모드 1의 MAC 연산 결과(점수, 시간, 판정)를 출력합니다.

    [동점 처리 - 모드 1]
      모드 1에서는 '판정 불가'로 표시합니다.
      (모드 2에서는 'UNDECIDED'로 표시하고 FAIL로 집계 — 요구사항에 따른 차이)
    """
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_time_ms:.3f} ms")
    if abs(score_a - score_b) < EPSILON:
        print("판정: UNDECIDED")
    elif score_a > score_b:
        print("판정: A")
    else:
        print("판정: B")


def mode1_user_input() -> None:
    """
    [모드 1] 사용자가 3×3 필터 2개(A, B)와 패턴을 직접 입력합니다.

    [실행 흐름]
      필터 A 입력 → 필터 B 입력 → 패턴 입력 → MAC 연산(10회 반복) → 결과 판정 출력
    """
    print_section_header(1, "필터 입력")
    filter_a: Matrix = input_nxn_matrix("필터 A")
    filter_b: Matrix = input_nxn_matrix("필터 B")

    print_section_header(2, "패턴 입력")
    pattern: Matrix = input_nxn_matrix("패턴")

    print_section_header(3, "MAC 결과")
    score_a: float
    time_a: float
    score_a, time_a = measure_mac_time(pattern, filter_a)
    score_b: float
    time_b: float
    score_b, time_b = measure_mac_time(pattern, filter_b)
    avg_time: float = (time_a + time_b) / 2
    print_mode1_result(score_a, score_b, avg_time)


# ================================================================
# 6. 모드 2 - data.json 분석
# ================================================================

def load_json_data(filepath: str) -> dict | None:
    """
    JSON 파일을 읽어 dict로 반환합니다. 실패 시 None을 반환합니다.

    [에러 처리]
      파일 미존재, 인코딩 오류, JSON 파싱 실패 등 모든 예외를 잡아
      프로그램이 비정상 종료되지 않도록 합니다.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        return data
    except Exception as e:
        print(f"data.json 파일을 읽을 수 없습니다: {e}")
        return None


def print_filter_load_status(filters: dict[str, dict]) -> None:
    """로드된 필터 목록을 콘솔에 출력합니다."""
    for f_key in filters.keys():
        print(f"✓ {f_key} 필터 로드 완료 (Cross, X)")


def extract_size_from_key(p_key: str) -> tuple[str, str]:
    """
    패턴 키('size_5_1')에서 크기 문자열과 필터 키를 추출합니다.

    [키 규칙]
      패턴 키: 'size_{N}_{idx}' 형식
      → N 추출 후 'size_{N}'으로 필터 매칭

    반환: (크기 문자열 N, 필터 키 'size_N')
    """
    parts: list[str] = p_key.split("_")
    n_str: str = parts[1] if len(parts) >= 2 else ""
    filter_key: str = f"size_{n_str}"
    return n_str, filter_key


def get_filter_matrices(
    filters: dict[str, dict], filter_key: str
) -> tuple[Matrix, Matrix]:
    """
    필터 딕셔너리에서 Cross/X 필터 행렬을 추출합니다.

    [키 정규화]
      data.json의 필터 키가 'cross'/'+'일 수도 있고 'x'/'X'일 수도 있으므로
      여러 가능한 키를 fallback으로 탐색합니다.
    """
    filter_data: dict = filters[filter_key]
    f_cross: Matrix = filter_data.get("cross", filter_data.get("+", []))
    f_x: Matrix = filter_data.get("x", filter_data.get("X", []))
    return f_cross, f_x


def validate_pattern_key(
    p_key: str, filters: dict[str, dict]
) -> tuple[bool, str, str, list[str]]:
    """
    패턴 키의 유효성을 검증합니다.

    [검증 항목]
      1. 키 형식: 'size_{N}_{idx}' 최소 2개 파트
      2. 해당 크기의 필터 존재 여부

    반환: (유효 여부, 크기 문자열, 필터 키, 실패 사유 리스트)
    """
    parts: list[str] = p_key.split("_")
    fail_reasons: list[str] = []
    if len(parts) < 2:
        fail_reasons.append(f"{p_key}: 잘못된 패턴 키 형식")
        return False, "", "", fail_reasons
    n_str: str
    filter_key: str
    n_str, filter_key = extract_size_from_key(p_key)
    if filter_key not in filters:
        fail_reasons.append(f"{p_key}: 필터 미존재")
        return False, n_str, filter_key, fail_reasons
    return True, n_str, filter_key, fail_reasons


def validate_pattern_size(
    p_key: str, pattern_input: Matrix, n: int
) -> tuple[bool, list[str]]:
    """
    패턴 행렬의 크기가 기대 크기(NxN)와 일치하는지 검증합니다.

    [검증 원리]
      행 수 == N이고, 모든 행의 열 수 == N인지 확인합니다.
      불일치 시 FAIL로 처리하되 프로그램은 중단하지 않습니다.
    """
    fail_reasons: list[str] = []
    if len(pattern_input) != n or any(len(row) != n for row in pattern_input):
        fail_reasons.append(f"{p_key}: 패턴 크기 불일치")
        return False, fail_reasons
    return True, fail_reasons


def analyze_single_pattern(
    p_key: str, p_data: dict, filters: dict[str, dict],
    perf_data: PerfDict
) -> tuple[bool, list[str]]:
    """
    단일 패턴에 대해 검증 → MAC 연산 → 판정을 수행합니다.

    [반환값]
      (PASS 여부, 실패 사유 리스트)

    [동점 처리 - 모드 2]
      UNDECIDED가 나오면 expected와 일치하지 않으므로 무조건 FAIL로 집계됩니다.
    """
    print(f"--- {p_key} ---")
    is_valid, n_str, filter_key, fails = validate_pattern_key(p_key, filters)
    if not is_valid:
        print(f"  {fails[0].split(': ')[1]}. FAIL")
        return False, fails

    pattern_input: Matrix = p_data.get("input", [])
    n: int = int(n_str) if n_str.isdigit() else 0
    is_valid, fails = validate_pattern_size(p_key, pattern_input, n)
    if not is_valid:
        print(f"  패턴 크기 불일치 (예상: {n}x{n}). FAIL")
        return False, fails

    return run_mac_and_judge(p_key, p_data, filters, filter_key, pattern_input, n, perf_data)


def run_mac_and_judge(
    p_key: str, p_data: dict, filters: dict[str, dict],
    filter_key: str, pattern_input: Matrix, n: int,
    perf_data: PerfDict
) -> tuple[bool, list[str]]:
    """
    검증 통과 후 MAC 연산을 수행하고 expected와 비교하여 PASS/FAIL을 판정합니다.

    [성능 데이터 축적]
      같은 크기의 패턴들의 연산 시간을 perf_data에 누적하여
      이후 크기별 평균 시간을 계산할 수 있도록 합니다.
    """
    f_cross, f_x = get_filter_matrices(filters, filter_key)
    score_cross, time_cross = measure_mac_time(pattern_input, f_cross)
    score_x, time_x = measure_mac_time(pattern_input, f_x)
    accumulate_perf_data(perf_data, filter_key, (time_cross + time_x) / 2, n)
    print(f"  Cross 점수: {score_cross}")
    print(f"  X 점수: {score_x}")
    expected: str = normalize_label(p_data.get("expected", ""))
    decision: str = decide_result(score_cross, score_x)
    return evaluate_decision(p_key, decision, expected)


def accumulate_perf_data(
    perf_data: PerfDict, filter_key: str, elapsed_ms: float, n: int
) -> None:
    """크기별 성능 데이터(시간 합계, 측정 횟수)를 누적합니다."""
    if filter_key not in perf_data:
        perf_data[filter_key] = {"time_sum": 0.0, "count": 0, "n": n}
    perf_data[filter_key]["time_sum"] += elapsed_ms
    perf_data[filter_key]["count"] += 1


def evaluate_decision(
    p_key: str, decision: str, expected: str
) -> tuple[bool, list[str]]:
    """
    판정 결과를 expected와 비교하여 PASS/FAIL을 출력하고 반환합니다.

    [FAIL 사유 분류]
      - '동점 규칙': UNDECIDED (epsilon 내 동점)
      - '오답': 판정은 내렸으나 expected와 불일치
    """
    if decision == expected:
        print(f"  판정: {decision} | expected: {expected} | PASS")
        return True, []
    reason: str = "동점 규칙" if decision == "UNDECIDED" else "오답"
    print(f"  판정: {decision} | expected: {expected} | FAIL ({reason})")
    return False, [f"{p_key}: {reason}으로 인한 FAIL"]


def print_performance_table(perf_data: PerfDict) -> None:
    """
    크기별 성능 분석 표를 출력합니다.

    [표 구성]
      크기(N×N) | 평균 시간(ms) | 연산 횟수(N²)
      연산 횟수 = N² 이므로 크기가 2배가 되면 연산은 4배 증가합니다(O(N²)).
    """
    print_section_header(3, "성능 분석 (평균/10회)")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수'}")
    print("-" * 40)
    sorted_items: list = sorted(perf_data.items(), key=lambda x: x[1]["n"])
    for f_key, data in sorted_items:
        n: int = int(data["n"])
        count: int = int(data["count"])
        if count > 0:
            avg_time: float = float(data["time_sum"]) / count
            print(f"{n}x{n:<8} {avg_time:<15.3f} {n * n}")


def print_test_summary(
    total: int, passed: int, failed: int, fail_cases: list[str]
) -> None:
    """전체 테스트 결과 요약(통과/실패 수, 실패 케이스 목록)을 출력합니다."""
    print_section_header(4, "결과 요약")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")
    if failed > 0:
        print("\n실패 케이스:")
        for fc in fail_cases:
            print(f"- {fc}")


def run_all_pattern_tests(
    patterns: dict[str, dict], filters: dict[str, dict]
) -> tuple[int, int, int, list[str], PerfDict]:
    """
    모든 패턴에 대해 순회하며 MAC 연산 및 PASS/FAIL 판정을 수행합니다.

    반환: (총 테스트 수, 통과 수, 실패 수, 실패 사유 리스트, 성능 데이터)
    """
    total: int = 0
    passed: int = 0
    failed: int = 0
    fail_cases: list[str] = []
    perf_data: PerfDict = {}
    for p_key, p_data in patterns.items():
        total += 1
        is_pass, reasons = analyze_single_pattern(p_key, p_data, filters, perf_data)
        if is_pass:
            passed += 1
        else:
            failed += 1
            fail_cases.extend(reasons)
    return total, passed, failed, fail_cases, perf_data


def mode2_json_analysis() -> None:
    """
    [모드 2] data.json에서 필터와 패턴을 로드하여 일괄 분석합니다.

    [실행 흐름]
      필터 로드 → 패턴 순회(키 검증 → 크기 검증 → MAC 연산 → 판정)
      → 성능 분석 표 출력 → 결과 요약 출력
    """
    data: dict | None = load_json_data("data.json")
    if data is None:
        return
    filters: dict[str, dict] = data.get("filters", {})
    patterns: dict[str, dict] = data.get("patterns", {})
    print_section_header(1, "필터 로드")
    print_filter_load_status(filters)
    print_section_header(2, "패턴 분석 (라벨 정규화 적용)")
    total, passed, failed, fail_cases, perf_data = run_all_pattern_tests(patterns, filters)
    print_performance_table(perf_data)
    print_test_summary(total, passed, failed, fail_cases)


# ================================================================
# 7. 메인 엔트리포인트
# ================================================================

def main() -> None:
    """
    프로그램 진입점. 모드(1: 사용자 입력 / 2: JSON 분석)를 선택합니다.

    [프로그램 전체 구조]
      main() → mode1_user_input() 또는 mode2_json_analysis()
      각 모드는 독립적으로 동작하며, 잘못된 선택 시 안내 메시지를 출력합니다.
    """
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
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
