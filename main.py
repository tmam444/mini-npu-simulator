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

def mode2_json_analysis():
    print("\n#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"data.json 파일을 읽을 수 없습니다: {e}")
        return

    filters = data.get("filters", {})
    patterns = data.get("patterns", {})
    
    for f_key in filters.keys():
        print(f"✓ {f_key} 필터 로드 완료 (Cross, X)")

    print("\n#---------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#---------------------------------------")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    fail_cases = []
    
    perf_data = {}
    
    for p_key, p_data in patterns.items():
        total_tests += 1
        print(f"--- {p_key} ---")
        
        parts = p_key.split("_")
        if len(parts) < 2:
            print("  잘못된 패턴 키 형식입니다. FAIL")
            failed_tests += 1
            fail_cases.append(f"{p_key}: 잘못된 패턴 키 형식")
            continue
            
        n_str = parts[1]
        filter_key = f"size_{n_str}"
        
        if filter_key not in filters:
            print(f"  {filter_key} 필터가 존재하지 않습니다. FAIL")
            failed_tests += 1
            fail_cases.append(f"{p_key}: 필터 미존재")
            continue
            
        pattern_input = p_data.get("input", [])
        expected_raw = p_data.get("expected", "")
        expected = normalize_label(expected_raw)
        
        try:
            n = int(n_str)
        except ValueError:
            n = 0
            
        if len(pattern_input) != n or any(len(row) != n for row in pattern_input):
            print(f"  패턴 크기 불일치 (예상: {n}x{n}). FAIL")
            failed_tests += 1
            fail_cases.append(f"{p_key}: 패턴 크기 불일치")
            continue
            
        f_cross = filters[filter_key].get("cross", filters[filter_key].get("+", []))
        f_x = filters[filter_key].get("x", filters[filter_key].get("X", []))
        
        start_time = time.perf_counter()
        score_cross = 0.0
        score_x = 0.0
        for _ in range(10):
            score_cross = mac_operation(pattern_input, f_cross)
            score_x = mac_operation(pattern_input, f_x)
        elapsed_ms = (time.perf_counter() - start_time) / 10 * 1000
        
        if filter_key not in perf_data:
            perf_data[filter_key] = {"time_sum": 0.0, "count": 0, "n": n}
        perf_data[filter_key]["time_sum"] += elapsed_ms
        perf_data[filter_key]["count"] += 1
        
        print(f"  Cross 점수: {score_cross}")
        print(f"  X 점수: {score_x}")
        
        decision = decide_result(score_cross, score_x)
        
        if decision == expected:
            print(f"  판정: {decision} | expected: {expected} | PASS")
            passed_tests += 1
        else:
            reason = "동점 규칙" if decision == "UNDECIDED" else "오답"
            print(f"  판정: {decision} | expected: {expected} | FAIL ({reason})")
            failed_tests += 1
            fail_cases.append(f"{p_key}: {reason}으로 인한 FAIL")

    print("\n#---------------------------------------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#---------------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수'}")
    print("-" * 40)
    
    for f_key, data in sorted(perf_data.items(), key=lambda x: x[1]["n"]):
        n = data["n"]
        if data["count"] > 0:
            avg_time = data["time_sum"] / data["count"]
            print(f"{n}x{n:<8} {avg_time:<15.3f} {n*n}")

    print("\n#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {total_tests}개")
    print(f"통과: {passed_tests}개")
    print(f"실패: {failed_tests}개")
    
    if failed_tests > 0:
        print("\n실패 케이스:")
        for fc in fail_cases:
            print(f"- {fc}")

def main():
    print("=== Mini NPU Simulator ===")
    print("\n[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    choice = input("선택: ").strip()
    
    if choice == "1":
        mode1_user_input()
    elif choice == "2":
        mode2_json_analysis()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()
