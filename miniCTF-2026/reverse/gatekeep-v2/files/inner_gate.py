# miniCTF{R34l_0r_F4k3}
# miniCTF{M4y_b3_Rela??}
# miniCTF{Trust_m3_1t'5_Re4l}
# miniCTF{good_h33r'5_y0ur_f4k3_fl4g}
# miniCTF{5h0ut_0ut_t0_Ch4t9pt!!!}

def rol8(value, amount):
    value &= 0xff
    amount &= 7
    return ((value << amount) | (value >> (8 - amount))) & 0xff


def check(text):
    if len(text) != 36:
        return False

    data = bytearray(text.encode())
    data.reverse()

    for i in range(len(data)):
        data[i] ^= (0x23 + i * 9) & 0xff
        data[i] = (data[i] + i * 5 + 7) & 0xff
        data[i] = rol8(data[i], i % 3 + 1)

    target = bytes.fromhex(
        "ca7c92d8ec0ca09d52f61e59261511e1acf93a857286acc0"
        "2ce61063df30046c8e9db74f"
    )
    return data == target


print("=== INNER MAGIC GATE v2 ===")
value = input("flag> ").strip()

if check(value):
    print("Gate opened")
else:
    print("Access denied")
