import gzip
import unicodedata
from PIL import Image

# Bước 1: key = chữ cái đầu mỗi câu của bản gốc, bỏ dấu, viết thường
poem = open("files/poetry.txt", encoding="utf-8").read().splitlines()
start = poem.index(next(l for l in poem if l.startswith("Bản gốc"))) + 1
lines = poem[start:start + 8]
strip = lambda s: unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
key = "".join(strip(l)[0] for l in lines).lower().encode()
print("key:", key)

# Bước 2: đọc LSB kênh Red, duyệt từng hàng
im = Image.open("files/bau_troi.png").convert("RGB")
w, h = im.size
px = im.load()
bits = [px[x, y][0] & 1 for y in range(h) for x in range(w)]
data = bytes(int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8))

# Bước 3: header = magic "Myna1" + độ dài 2 byte big-endian
assert data[:5] == b"Myna1"
n = int.from_bytes(data[5:7], "big")
payload = data[7:7 + n]

# Bước 4: XOR với key rồi giải nén gzip
plain = bytes(c ^ key[i % len(key)] for i, c in enumerate(payload))
print(gzip.decompress(plain).decode())
