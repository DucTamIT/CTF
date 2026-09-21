import base64
import string

# bird_memory.txt: bảng chữ cái gồm 64 emoji + 1 emoji padding (🥚)
emoji = list(open("files/bird_memory.txt", encoding="utf-8").read().strip())
journey = list(open("files/journey.txt", encoding="utf-8").read().strip())

# Map emoji thứ i sang ký tự thứ i của bảng Base64 chuẩn
b64 = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/="
encoded = "".join(b64[emoji.index(e)] for e in journey)
print("base64:", encoded)
print("flag:  ", base64.b64decode(encoded).decode())
