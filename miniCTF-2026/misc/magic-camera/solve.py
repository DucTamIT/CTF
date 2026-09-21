import hashlib
import struct
import numpy as np
from PIL import Image

# ---- Bước 1: đảo ngược decode_key ----
# sha256(decoded_key) == 17d455f9...7fd1, tra online ra "beautifulflowers"
decoded = b"beautifulflowers"
assert hashlib.sha256(decoded).hexdigest() == \
    "17d455f9c7e19015861d996f0b88489f3ed8be71279239f4a946f686ac317fd1"

MASK = [0xDB, 0xEF, 0x3D, 0x41, 0xA1]

def rotl(v, r):
    r &= 7
    return ((v << r) | (v >> ((8 - r) & 7))) & 0xFF

key = []
for i, c in enumerate(decoded[::-1]):           # đảo lại std::reverse
    c = (c + i * 3 + 7) & 0xFF                  # đảo phép trừ
    c ^= MASK[i % 5]                            # XOR tự nghịch đảo
    c = rotl(c, (i % 7) + 1)                    # đảo rotate_right
    key.append(c)
print("input key:", bytes(key).decode())

# ---- Bước 2: chạy ./chall <key> data.bin recovered.png (Linux/WSL) ----

# ---- Bước 3: đọc LSB kênh Blue của ảnh đã khôi phục ----
a = np.array(Image.open("images/recovered.png").convert("RGB"))
data = np.packbits(a[:, :, 2].reshape(-1) & 1).tobytes()
assert data[:4] == b"LSB1"
n = struct.unpack(">I", data[4:8])[0]
print("flag:", data[8:8 + n].decode())
