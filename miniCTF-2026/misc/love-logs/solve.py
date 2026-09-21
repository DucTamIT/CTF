import re

log = open("files/love_logs.txt", encoding="utf-8").read()

# Lấy các mảnh FLAGART, bỏ trùng nhưng giữ thứ tự xuất hiện
parts = list(dict.fromkeys(re.findall(r"FLAGART: (\S+)", log)))
cipher = "".join(parts)
print("cipher:", cipher)

# Caesar: dịch lùi 4 (q -> m, m -> i, ...)
def shift(c, k):
    if c.islower():
        return chr((ord(c) - 97 - k) % 26 + 97)
    if c.isupper():
        return chr((ord(c) - 65 - k) % 26 + 65)
    return c

print("flag:  ", "".join(shift(c, 4) for c in cipher))
