from __future__ import annotations
from typing import Dict, List, Union

# ──────────────────────────────────────────────
# 타입 별칭 정의
# ──────────────────────────────────────────────
Matrix = List[List[float]]
PerfDict = Dict[str, Dict[str, Union[float, int]]]

# ──────────────────────────────────────────────
# 상수 정의
# ──────────────────────────────────────────────
EPSILON: float = 1e-9          # 부동소수점 비교 허용오차
REPEAT_COUNT: int = 10         # 성능 측정 반복 횟수
MODE1_SIZE: int = 3            # 모드 1 행렬 크기 고정값
