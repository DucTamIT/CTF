M = 0xFFFFFFFF

# Hàm calculate() trong binary
def calculate(x):
    x ^= 0x5A5A
    x = (x + 0x1337) & M
    x = (x * 7) & M          # shl 3 ; sub  ->  x*8 - x
    x = (x - 0x2468) & M
    x ^= 0x1F2E3D
    return x

TARGET = 0xCACDB             # giá trị get_target() trả về

# Đảo ngược từng bước (7 khả nghịch mod 2^32)
x = TARGET ^ 0x1F2E3D
x = (x + 0x2468) & M
x = (x * pow(7, -1, 1 << 32)) & M
x = (x - 0x1337) & M
x ^= 0x5A5A

assert calculate(x) == TARGET
print("answer:", x)

# Sửa magic "ME" -> "MZ" để chạy được file exe
data = bytearray(open("files/Black_Crow.exe", "rb").read())
data[:2] = b"MZ"
open("Black_Crow_fixed.exe", "wb").write(data)
print("wrote Black_Crow_fixed.exe, run it and enter", x)
