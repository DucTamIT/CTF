# Giải ngược GateKeep v1: đảo lại đúng các phép biến đổi mà g() áp lên input.
def rol(x, n): n &= 7; return ((x << n) | (x >> ((8 - n) & 7))) & 255
def ror(x, n): return rol(x, (8 - (n & 7)) & 7)

z = (58, 137, 253, 162, 111, 80, 236, 126, 97, 52,
     80, 106, 107, 73, 122, 42, 176, 153, 39, 169,
     28, 65, 82, 180, 150, 122, 39, 198, 239, 20)

# (5) đảo xor-chain: new[i] = old[i] ^ (0xA7 nếu i==0, ngược lại old[i-1])
c = list(z)
old = [c[0] ^ 0xA7]
for i in range(1, 30):
    old.append(c[i] ^ old[i - 1])
c = old

# (4) đảo split c = b[::2] + b[1::2][::-1]
even, odd = c[:15], c[15:][::-1]
b = [0] * 30
for i in range(15):
    b[2 * i], b[2 * i + 1] = even[i], odd[i]

# (3) đảo: b[i] = rol(b[i], i%5+1); b[i] += i*7+13
for i in range(30):
    b[i] = ror((b[i] - (i * 7 + 13)) & 255, i % 5 + 1)

# (2) đảo xor mask
for i in range(30):
    b[i] ^= (i * 11 + 0x35) & 255

# (1) đảo reverse
print("flag:", bytes(b[::-1]).decode())
