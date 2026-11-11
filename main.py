# Mini NPU Simulator

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
