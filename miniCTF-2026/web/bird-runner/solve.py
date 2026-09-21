# Bird Runner: gửi điểm >= 1 tỉ với checksum tự tính (thuật toán zx lấy từ game.js).
import json
import urllib.request

BASE = "http://103.116.52.180:20909"
M = 0xFFFFFFFF
K1, K2, K3, K4, K5 = 0x9E3779B9, 0x165667B1, 0x85EBCA6B, 0x2545F491, 0x27D4EB2F

def u32(x): return x & M
def imul(a, b): return u32(u32(a) * u32(b))
def rotl(x, n): x = u32(x); return u32((x << n) | (x >> (32 - n)))

def zx(token, value, nonce):
    msg = f"{token}|{value}|{nonce}"
    a, b = 0x1505, K1
    for ch in msg:
        c = ord(ch)
        a = rotl(u32(imul(a, 33) ^ c), 13)
        b = rotl(u32(imul(u32(b ^ u32(c + K2)), K3)), 25)
        a = u32(a + b)
    a = u32(a ^ (a >> 15)); a = imul(a, K4); a = u32(a ^ (a >> 13))
    b = u32(b ^ (b >> 16)); b = imul(b, K5); b = u32(b ^ (b >> 11))
    return format(a, "08x") + format(b, "08x")

def post(path, data=None):
    req = urllib.request.Request(BASE + path, method="POST",
        data=None if data is None else json.dumps(data).encode(),
        headers={} if data is None else {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=15))

s = post("/api/game/start")
score = 1_000_000_000
cs = zx(s["token"], score, s["nonce"])
res = post("/api/game/submit", {"session_id": s["session_id"], "score": score, "checksum": cs})
print("flag:", res.get("flag"))
