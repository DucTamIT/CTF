import base64
import io
import re
import struct
import zipfile

import numpy as np
from PIL import Image

# Bước 1: file txt là hex dump của một PNG
data = bytes.fromhex(open("files/chan.txt").read())

# PNG chính kết thúc ở IEND, phía sau là 1 file zip rồi 1 PNG nữa
i = 8
while True:
    n, t = struct.unpack(">I4s", data[i:i + 8])
    if t == b"tEXt":
        print("[decoy] tEXt:", data[i + 8:i + 8 + n].split(b"\0")[1].decode())
    i += 12 + n
    if t == b"IEND":
        break
main_png, rest = data[:i], data[i:]
zip_end = rest.find(b"PK\x05\x06") + 22
zf, third_png = rest[:zip_end], rest[zip_end:]

z = zipfile.ZipFile(io.BytesIO(zf))
print("notes.txt:", z.read("notes.txt").decode().strip())
preview = base64.b64decode(z.read("img_payload.txt"))

# Decoy thứ 2: RGB-LSB của PNG nằm sau zip
t = np.array(Image.open(io.BytesIO(third_png)).convert("RGB"))
lsb = np.packbits((t & 1).reshape(-1)).tobytes()
print("[decoy] third.png RGB-LSB:", re.search(rb"minictf\{[^}]*\}", lsb).group().decode())

# Bước 2: flag thật là CHỮ vẽ trong bit plane 0
Image.fromarray((np.array(Image.open(io.BytesIO(main_png)).convert("RGB"))[:, :, 0] & 1) * 255) \
    .save("chan_R0.png")        # nửa đầu: LSB kênh Red của PNG chính
Image.fromarray((np.array(Image.open(io.BytesIO(preview)).convert("RGB"))[:, :, 1] & 1) * 255) \
    .save("preview_G0.png")     # nửa sau: LSB kênh Green của ảnh preview
print("Đã lưu chan_R0.png và preview_G0.png, mở ra đọc flag")
