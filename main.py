# Mini NPU Simulator

import json
import time

def mac(pattern, filt):
    """패턴과 필터의 같은 위치 값끼리 곱하고, 그 값을 모두 더해 점수를 돌려준다."""
    n = len(pattern)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total

# 1e-9는 1 × 10⁻⁹ = 0.000000001
EPSILON = 1e-9

def judge(score_a, score_b, label_a, label_b):
    """두 점수를 비교해 더 큰 쪽 라벨을 돌려준다. 차이가 EPSILON보다 작으면 동점(UNDECIDED)이다."""
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    if score_a > score_b:
        return label_a
    return label_b

REPEAT = 10

def measure_ms(pattern, filt):
    """mac을 REPEAT번 실행한 평균 시간(ms)을 돌려준다."""
    start = time.perf_counter()
    for _ in range(REPEAT):
        mac(pattern, filt)
    return (time.perf_counter() - start) / REPEAT * 1000

def section(title):
    """구역 제목을 출력한다."""
    print()
    print("#" + "-" * 40)
    print(f"# {title}")
    print("#" + "-" * 40)

def read_matrix(title, n):
    """n줄을 한 줄씩 입력받아 n×n 리스트로 돌려준다. 틀린 줄은 그 줄만 다시 입력받는다."""
    example = " ".join(["1"] * n)
    print(f"{title} ({n}줄 입력, 공백 구분, 예: {example})")
    matrix = []
    while len(matrix) < n:
        row_no = len(matrix) + 1
        parts = input(f"{row_no}번째 줄: ").split()
        try:
            row = [float(value) for value in parts]
        except ValueError:
            row = []
        if len(row) != n:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요. (예: {example})")
            print(f"→ {row_no}번째 줄을 다시 입력하세요.")
            continue
        matrix.append(row)
    return matrix

def print_matrix(name, matrix):
    """저장된 2차원 리스트를 한 줄씩 출력한다."""
    print(f"{name} 저장 완료:")
    for row in matrix:
        print("  " + " ".join(str(value) for value in row))


def print_performance(results):
    """(크기 n, 평균 ms) 목록을 표로 출력한다."""
    print("크기        평균 시간(ms)   연산 횟수")
    print("-" * 36)
    for n, ms in results:
        size = f"{n}×{n}"
        print(f"{size:<8}{ms:>14.4f}{n * n:>12}") 

def run_user_mode():
    """모드 1: 3×3 필터 A, B와 패턴을 입력받아 판정하고 성능을 출력한다."""
    section("[1] 필터 입력")
    filter_a = read_matrix("필터 A", 3)
    print_matrix("필터 A", filter_a)
    print()
    filter_b = read_matrix("필터 B", 3)
    print_matrix("필터 B", filter_b)

    section("[2] 패턴 입력")
    pattern = read_matrix("패턴", 3)
    print_matrix("패턴", pattern)   
    
    section("[3] MAC 결과")
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    ms = measure_ms(pattern, filter_a)
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{REPEAT}회): {ms:.4f} ms")
    result = judge(score_a, score_b, "A", "B")
    if result == "UNDECIDED":
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {result}")

    section(f"[4] 성능 분석 (평균/{REPEAT}회)")
    print_performance([(3, ms)])

DATA_FILE = "data.json"


def normalize_label(value):
    """'+'·'cross'는 Cross로, 'x'는 X로 바꾼다. 그 밖의 값은 None을 돌려준다."""
    text = str(value).strip().lower()
    if text in ("+", "cross"):
        return "Cross"
    if text == "x":
        return "X"
    return None

def is_square(matrix, n):
    """matrix가 n줄이고, 줄마다 n칸인 2차원 리스트인지 확인한다."""
    # isinstance(값, 타입) -> 값이 타입인지 검사하는 내장 함수
    if not isinstance(matrix, list) or len(matrix) != n:
        return False
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            return False
    return True

def load_filters(data):
    """filters의 size_N마다 {'Cross': 배열, 'X': 배열}을 만든다."""
    filters = {}
    for size_key, pair in data.get("filters", {}).items():
        if not isinstance(pair, dict):
            print(f"✗ {size_key:<7} 필터 형식 오류 (건너뜀)")
            continue
        filters[size_key] = {}
        for key, matrix in pair.items():
            label = normalize_label(key)
            if label is not None:
                filters[size_key][label] = matrix
        labels = ", ".join(filters[size_key])
        print(f"✓ {size_key:<7} 필터 로드 완료 ({labels})")
    return filters

def check_case(key, case, filters):
    """패턴 1개를 검사한다. 문제가 있으면 원인 문구를, 없으면 빈 문자열을 돌려준다."""
    parts = key.split("_")
    if len(parts) != 3 or parts[0] != "size" or not parts[1].isdigit():
        return f"키 형식 오류: {key}"
    n = int(parts[1])
    size_key = f"size_{n}"
    if size_key not in filters:
        return f"{size_key} 필터 없음"
    if not isinstance(case, dict) or "input" not in case or "expected" not in case:
        return "input 또는 expected 없음"
    if normalize_label(case["expected"]) is None:
        return f"알 수 없는 expected 라벨: {case['expected']}"
    if not is_square(case["input"], n):
        return f"크기 불일치: 패턴이 {n}×{n} 크기가 아님"
    for label in ("Cross", "X"):
        if not is_square(filters[size_key].get(label), n):
            return f"크기 불일치: {label} 필터가 {n}×{n} 크기가 아님"
    return ""

def analyze_case(key, case, filters):
    """패턴 1개의 점수·판정·PASS/FAIL을 출력한다. 실패 사유(PASS면 빈 문자열)를 돌려준다."""
    print(f"--- {key} ---")
    problem = check_case(key, case, filters)
    if problem:
        print(f"FAIL ({problem})")
        return problem
    size_filters = filters[f"size_{key.split('_')[1]}"]
    score_cross = mac(case["input"], size_filters["Cross"])
    score_x = mac(case["input"], size_filters["X"])
    result = judge(score_cross, score_x, "Cross", "X")
    expected = normalize_label(case["expected"])
    print(f"Cross 점수: {score_cross}")
    print(f"X 점수: {score_x}")
    if result == expected:
        print(f"판정: {result} | expected: {expected} | PASS")
        return ""
    reason = "동점 규칙" if result == "UNDECIDED" else "판정 불일치"
    print(f"판정: {result} | expected: {expected} | FAIL ({reason})")
    return reason

def run_json_mode():
    """모드 2: data.json의 패턴마다 Cross·X 점수를 구해 판정하고 PASS/FAIL을 출력한다."""
    try:
        with open(DATA_FILE, encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError) as error:
        print(f"{DATA_FILE}을 읽을 수 없습니다: {error}")
        return []

    section("[1] 필터 로드")
    filters = load_filters(data)

    section("[2] 패턴 분석 (라벨 정규화 적용)")
    results = []
    for key, case in data.get("patterns", {}).items():
        reason = analyze_case(key, case, filters)
        results.append((key, reason))

    run_performance()
    print_summary(results)
    return results


PERF_SIZES = [3, 5, 13, 25]

def make_cross(n):
    """n×n 십자가 배열(가운데 줄과 가운데 칸이 1)을 만든다."""
    mid = n // 2
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == mid or j == mid:
                row.append(1.0)
            else:
                row.append(0.0)
        matrix.append(row)
    return matrix

def run_performance():
    """크기별로 mac 평균 시간을 재고 표로 출력한다."""
    results = []
    for n in PERF_SIZES:
        matrix = make_cross(n)
        results.append((n, measure_ms(matrix, matrix)))
    section(f"[3] 성능 분석 (평균/{REPEAT}회)")
    print_performance(results)

def print_summary(results):
    """모드 2 결과 목록으로 총/통과/실패 수와 실패 케이스를 출력한다."""
    failed = []
    for key, reason in results:
        if reason:
            failed.append((key, reason))
    section("[4] 결과 요약")
    print(f"총 테스트: {len(results)}개")
    print(f"통과: {len(results) - len(failed)}개")
    print(f"실패: {len(failed)}개")
    if failed:
        print()
        print("실패 케이스:")
        for key, reason in failed:
            print(f"- {key}: FAIL ({reason})")


def main():
    """모드를 고르고, 고른 모드를 실행한다."""
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    while True:
        choice = input("선택: ").strip()
        if choice == "1":
            run_user_mode()
            break
        if choice == "2":
            run_json_mode()
            break
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()