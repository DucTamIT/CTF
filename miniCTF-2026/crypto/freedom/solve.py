# Cánh 1 — Knapsack: c = 42, a = [1, 2, 4, 8, 16, 32]
a, c = [1, 2, 4, 8, 16, 32], 42
x = [(c >> i) & 1 for i in range(6)]          # a là lũy thừa của 2 -> chính là bit của c
assert sum(ai * xi for ai, xi in zip(a, x)) == c
print("Cánh 1:", "".join(map(str, x)))

# Cánh 2 — ECDSA nonce reuse
h1, h2, s1, s2, n, r = 7, 4, 5, 2, 23, 11
k = (h1 - h2) * pow(s1 - s2, -1, n) % n
priv = (s1 * k - h1) * pow(r, -1, n) % n
print("Cánh 2:", priv, f"(k = {k})")

# Cánh 3 — LFSR 16-bit, taps 16,15,13,4, output = MSB, dịch trái
obs = [1, 0, 1, 1, 0, 1, 0, 0]

def lfsr(state, n):
    out = []
    for _ in range(n):
        out.append((state >> 15) & 1)
        fb = 0
        for t in (16, 15, 13, 4):
            fb ^= (state >> (16 - t)) & 1
        state = ((state << 1) | fb) & 0xFFFF
    return out

state = int("".join(map(str, obs)), 2) << 8   # 8 bit output đầu = 8 bit cao của state
assert lfsr(state, 8) == obs
print("Cánh 3:", f"{state:016b}")
