# Flag của Hieeusuuuuuiiiiii được decode() dựng trên stack từ vài movabs rồi XOR 0x37.
buf = bytearray(39)
def put(off, q):
    for i in range(8):
        buf[off + i] = (q >> (8 * i)) & 0xFF

# 5 immediate movabs trong decode() (cái ở -0x41 ghi đè 1 byte cuối của khối trước)
put(0,  0x4C7163745E595E5A)
put(8,  0x4C7163745E595E5A)
put(16, 0x4C7163745E595E5A)
put(24, 0x4255685841685E44)
put(31, 0x4A4A4A435E5B6842)

print("flag:", bytes(b ^ 0x37 for b in buf).decode())
