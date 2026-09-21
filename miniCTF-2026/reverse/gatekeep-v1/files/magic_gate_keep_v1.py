def r(x, n):
    n &= 7
    return ((x << n) | (x >> ((8 - n) & 7))) & 255


def g(a):
    p = 17
    b = bytearray()
    q = (sum(a.encode()) << 1) ^ len(a)

    while True:
        if p == 17:
            if len(a.encode()) != 30:
                return False
            b = bytearray(a.encode())
            b.reverse()
            for i in range(len(b)):
                b[i] ^= (i * 11 + 0x35) & 255
            p = 2

        elif p == 2:
            if 3 * 7 == 21:
                p = 28
            else:
                p = 23

        elif p == 28:
            if q - q == 0:
                p = 11
            else:
                p = 4

        elif p == 11:
            if 1 << 5 == 32:
                p = 6
            else:
                p = 19

        elif p == 6:
            if (len(a) | 0) == len(a):
                p = 20
            else:
                p = 23

        elif p == 20:
            if (q ^ q) == 0:
                p = 0
            else:
                p = 4

        elif p == 0:
            if all(x == x for x in range(3)):
                p = 25
            else:
                p = 23

        elif p == 25:
            if not (False and q):
                p = 9
            else:
                p = 4

        elif p == 9:
            if 0 <= len(a):
                p = 14
            else:
                p = 23

        elif p == 14:
            if (q & 0) == 0:
                p = 3
            else:
                p = 4

        elif p == 3:
            if ((q | 1) & 1) == 1:
                p = 4
            else:
                p = 23

        elif p == 4:
            for i in range(len(b)):
                b[i] = r(b[i], i % 5 + 1)
                b[i] = (b[i] + i * 7 + 13) & 255
            p = 22

        elif p == 22:
            if sum((1, 2, 3)) == 6:
                p = 7
            else:
                p = 23

        elif p == 7:
            if 2 ** 5 == 32:
                p = 18
            else:
                p = 4

        elif p == 18:
            if "gate"[::-1] == "etag":
                p = 1
            else:
                p = 23

        elif p == 1:
            if ord("A") + 1 == 66:
                p = 26
            else:
                p = 4

        elif p == 26:
            if bool(1):
                p = 12
            else:
                p = 23

        elif p == 12:
            if not (None is not None):
                p = 29
            else:
                p = 4

        elif p == 29:
            if q * 0 == 0:
                p = 5
            else:
                p = 23

        elif p == 5:
            if len({1, 2, 3}) == 3:
                p = 15
            else:
                p = 4

        elif p == 15:
            if min(4, 9) == 4:
                p = 10
            else:
                p = 23

        elif p == 10:
            if max(4, 9) == 9:
                p = 24
            else:
                p = 4

        elif p == 24:
            if q // 1 == q:
                p = 8
            else:
                p = 23

        elif p == 8:
            if q % 1 == 0:
                p = 21
            else:
                p = 4

        elif p == 21:
            if (5 & 3) == 1:
                p = 13
            else:
                p = 23

        elif p == 13:
            if (8 >> 1) == 4:
                p = 27
            else:
                p = 4

        elif p == 27:
            if ((q * q + q) & 1) == 0:
                p = 16
            else:
                p = 23

        elif p == 16:
            if (q * q) % 4 != 2:
                p = 19
            else:
                p = 4

        elif p == 19:
            if abs(-7) == 7:
                p = 23
            else:
                p = 4

        elif p == 23:
            c = b[::2] + b[1::2][::-1]
            c = bytearray(x ^ (0xA7 if i == 0 else c[i - 1]) for i, x in enumerate(c))
            z = (
                58, 137, 253, 162, 111, 80, 236, 126, 97, 52,
                80, 106, 107, 73, 122, 42, 176, 153, 39, 169,
                28, 65, 82, 180, 150, 122, 39, 198, 239, 20
            )
            return tuple(c) == z

        else:
            return False


print("=== MAGIC GATE KEEP v1 ===")
if g(x := input("key> ").strip()):
    print("Gate opened")
else:
    print("Access denied")
