# GateKeep v2: đảo ngược check() của inner gate ẩn trong payload_3.
def rol8(v, a): v &= 255; a &= 7; return ((v << a) | (v >> (8 - a))) & 255
def ror8(v, a): return rol8(v, (8 - (a & 7)) & 7)

target = bytes.fromhex(
    "ca7c92d8ec0ca09d52f61e59261511e1acf93a857286acc0"
    "2ce61063df30046c8e9db74f"
)

d = bytearray(target)
for i in range(len(d)):
    d[i] = ror8(d[i], i % 3 + 1)      # đảo rol8
    d[i] = (d[i] - (i * 5 + 7)) & 255  # đảo cộng
    d[i] ^= (0x23 + i * 9) & 255       # đảo xor
d.reverse()                            # đảo reverse

print("flag:", d.decode())
