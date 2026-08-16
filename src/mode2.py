from __future__ import annotations
import os
from custom_types import Matrix, PerfDict
from core import normalize_label, decide_result, measure_mac_time
from utils import load_json_data, print_section_header

def print_filter_load_status(filters: dict[str, dict]) -> None:
    for f_key in filters.keys():
        print(f"✓ {f_key} 필터 로드 완료 (Cross, X)")

def extract_size_from_key(p_key: str) -> tuple[str, str]:
    parts: list[str] = p_key.split("_")
    n_str: str = parts[1] if len(parts) >= 2 else ""
    filter_key: str = f"size_{n_str}"
    return n_str, filter_key

def get_filter_matrices(filters: dict[str, dict], filter_key: str) -> tuple[Matrix, Matrix]:
    filter_data: dict = filters[filter_key]
    f_cross: Matrix = filter_data.get("cross", filter_data.get("+", []))
    f_x: Matrix = filter_data.get("x", filter_data.get("X", []))
    return f_cross, f_x

def validate_pattern_key(p_key: str, filters: dict[str, dict]) -> tuple[bool, str, str, list[str]]:
    parts: list[str] = p_key.split("_")
    fail_reasons: list[str] = []
    if len(parts) < 2:
        fail_reasons.append(f"{p_key}: 잘못된 패턴 키 형식")
        return False, "", "", fail_reasons
    n_str, filter_key = extract_size_from_key(p_key)
    if filter_key not in filters:
        fail_reasons.append(f"{p_key}: 필터 미존재")
        return False, n_str, filter_key, fail_reasons
    return True, n_str, filter_key, fail_reasons

def validate_pattern_size(p_key: str, pattern_input: Matrix, n: int) -> tuple[bool, list[str]]:
    fail_reasons: list[str] = []
    if len(pattern_input) != n or any(len(row) != n for row in pattern_input):
        fail_reasons.append(f"{p_key}: 패턴 크기 불일치")
        return False, fail_reasons
    return True, fail_reasons

def evaluate_decision(p_key: str, decision: str, expected: str, score_diff: float = 0.0) -> tuple[bool, list[str]]:
    if decision == expected:
        print(f"  판정: expected: {expected} | PASS")
        return True, []
    
    if decision == "UNDECIDED":
        print(f"  [Info] 동점 원인 분석 - 두 점수 차이: {score_diff:.2e}")
        reason = "동점 규칙"
        print(f"  판정: {decision} | FAIL ({reason})")
    else:
        reason = "오답"
        print(f"  판정: {decision} | expected: {expected} | FAIL ({reason})")
        
    return False, [f"{p_key}: {reason}으로 인한 FAIL"]

def accumulate_perf_data(perf_data: PerfDict, filter_key: str, elapsed_ms: float, n: int) -> None:
    if filter_key not in perf_data:
        perf_data[filter_key] = {"time_sum": 0.0, "count": 0, "n": n}
    perf_data[filter_key]["time_sum"] += elapsed_ms
    perf_data[filter_key]["count"] += 1

def run_mac_and_judge(
    p_key: str, p_data: dict, filters: dict[str, dict],
    filter_key: str, pattern_input: Matrix, n: int, perf_data: PerfDict
) -> tuple[bool, list[str]]:
    f_cross, f_x = get_filter_matrices(filters, filter_key)
    score_cross, time_cross = measure_mac_time(pattern_input, f_cross)
    score_x, time_x = measure_mac_time(pattern_input, f_x)
    accumulate_perf_data(perf_data, filter_key, (time_cross + time_x) / 2, n)
    print(f"  Cross 점수: {score_cross}")
    print(f"  X 점수: {score_x}")
    expected: str = normalize_label(p_data.get("expected", ""))
    decision: str = decide_result(score_cross, score_x)
    score_diff: float = abs(score_cross - score_x)
    return evaluate_decision(p_key, decision, expected, score_diff)

def analyze_single_pattern(
    p_key: str, p_data: dict, filters: dict[str, dict], perf_data: PerfDict
) -> tuple[bool, list[str]]:
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

def print_performance_table(perf_data: PerfDict) -> None:
    print_section_header(3, "성능 분석 (평균/10회)")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수'}")
    print("-" * 40)
    sorted_items = sorted(perf_data.items(), key=lambda x: x[1]["n"])
    for f_key, data in sorted_items:
        n, count = int(data["n"]), int(data["count"])
        if count > 0:
            avg_time: float = float(data["time_sum"]) / count
            print(f"{n}x{n:<8} {avg_time:<15.3f} {n * n}")

def print_test_summary(total: int, passed: int, failed: int, fail_cases: list[str]) -> None:
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
    total = passed = failed = 0
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
    """[모드 2] data.json에서 필터와 패턴을 로드하여 일괄 분석합니다."""
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path: str = os.path.join(base_dir, "data", "data.json")
    data: dict | None = load_json_data(json_path)
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
