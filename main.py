# Mini NPU Simulator

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
            print("data.json 분석 모드는 준비 중입니다.")
            break
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()