import struct

data = bytearray(open("files/image.jpeg", "rb").read())
print("header:", data[:8].hex(" "))

# Bước 1: sửa lại PNG signature bị xoá các byte ở vị trí lẻ
data[:8] = b"\x89PNG\r\n\x1a\n"
open("fixed.png", "wb").write(data)

# Bước 2: duyệt các chunk tới IEND, lấy phần dữ liệu thừa phía sau
i = 8
while True:
    n, t = struct.unpack(">I4s", data[i:i + 8])
    i += 12 + n
    if t == b"IEND":
        break
trailer = data[i:].decode().split()
print("trailer:", " ".join(trailer[:4]), "...")

# Bước 3: '0' -> 0, '2' -> 1, mỗi nhóm 8 bit là 1 ký tự
print("flag:", "".join(chr(int(g.replace("2", "1"), 2)) for g in trailer))
