# Mini NPU Simulator

def mac(pattern, filt):
    """패턴과 필터의 같은 위치 값끼리 곱하고, 그 값을 모두 더해 점수를 돌려준다."""
    n = len(pattern)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total