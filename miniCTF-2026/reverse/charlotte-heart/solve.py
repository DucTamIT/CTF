# Tính flag của Charlotte's Heart trực tiếp từ trạng thái đích của VM.
# Không cần mật khẩu: flag được giải mã từ các hằng số kiểm tra trong binary.
M = 0xFFFFFFFF
def rol(x, n):
    n &= 31
    return ((x << n) | (x >> (32 - n))) & M

# Điều kiện thắng tại 0x1400036be:
#   r0 == 0x537f9c1b  và  rol(r0,3) ^ r1 == 0xa39bc00a
r0 = 0x537F9C1B
r1 = rol(r0, 3) ^ 0xA39BC00A

# 55 byte keystream nguồn tại RVA 0x1400050c0
d = open("files/CharlotteHeart.exe", "rb").read()
T = d[0x1400050C0 - 0x140005000 + 0x3600:][:0x37]

# seed = rol(r1,7) ^ 0xc4a87c76, rồi PRNG xmxmx sinh keystream
seed = rol(r1, 7) ^ 0xC4A87C76
esi, out = seed, bytearray()
for ti in T:
    edx = rol(esi, 13) ^ esi
    esi = (edx * 0x9E3779B9) & M
    esi ^= esi >> 16
    out.append((ti ^ esi) & 0xFF)

print("flag: minictf{" + out.decode() + "}")
