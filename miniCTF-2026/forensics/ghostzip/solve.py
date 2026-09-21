import io
import re
from collections import Counter

import numpy as np
from PIL import Image

# Bước 1: "zip" thực chất là PNG, 8 byte signature bị thay bằng 7 byte rác -> ghi lại
raw = open("files/GhostOrSmth.zip", "rb").read()
print("header:", raw[:7].hex(" "))
img = Image.open(io.BytesIO(b"\x89PNG\r\n\x1a\n" + raw[7:])).convert("RGB")
print("image:", img.size)

# Bước 2: MSB (bit 7) của từng kênh R,G,B, đọc theo từng pixel, gom 8 bit thành 1 byte
a = np.array(img)[:1131]                      # payload nằm trong 1131 hàng đầu
bits = (a.reshape(-1) >> 7) & 1
text = np.packbits(bits).tobytes().decode("utf-8", "ignore")
print("payload:", len(text), "ký tự, mở đầu:", text[:60].replace("\n", " "))

# Bước 3: văn bản là vài đoạn lặp lại ~110 lần; ký tự được chèn thêm
# là ký tự mà mọi cửa sổ 16 ký tự chứa nó đều chỉ xuất hiện đúng 1 lần
W = 16
cnt = Counter(text[i:i + W] for i in range(len(text) - W + 1))
uniq = [cnt[text[i:i + W]] == 1 for i in range(len(text) - W + 1)]
odd = [all(uniq[j] for j in range(max(0, i - W + 1), min(i, len(uniq) - 1) + 1))
       for i in range(len(text))]
pieces = []
for m in re.finditer(r"1+", "".join("1" if o else "0" for o in odd)):
    pieces.append(text[m.start():m.end()])
print("fragments:", pieces)

# Bước 4: ghép lại và ROT-9 ngược (dịch lùi 9)
enc = "".join(pieces)
def rot(c, k):
    if c.islower(): return chr((ord(c) - 97 - k) % 26 + 97)
    if c.isupper(): return chr((ord(c) - 65 - k) % 26 + 65)
    return c
print("cipher:", enc)
print("flag:  ", "".join(rot(c, 9) for c in enc))
