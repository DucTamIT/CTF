import base64
import re
import struct
import subprocess

PCAP = "Emperor of Darkness.pcap"
TSHARK = r"C:\Program Files\Wireshark\tshark.exe"

# Bước 1: lấy body của 10 HTTP response từ port 8080 (SimpleHTTP)
out = subprocess.run(
    [TSHARK, "-r", PCAP, "-Y", "http.response && tcp.srcport==8080",
     "-T", "fields", "-e", "frame.number", "-e", "http.file_data"],
    capture_output=True, text=True).stdout
rows = sorted((l.split("\t") for l in out.splitlines()), key=lambda r: int(r[0]))

# Bước 2: mỗi response là 1 mảnh Base64 -> ghép theo thứ tự -> PNG
png = base64.b64decode("".join(bytes.fromhex(r[1]).decode().strip() for r in rows))
open("port8080.png", "wb").write(png)

# Bước 3: duyệt chunk, in tEXt (decoy) và eXIf UserComment (Base32)
i = 8
while i < len(png):
    n, t = struct.unpack(">I4s", png[i:i + 8])
    body = png[i + 8:i + 8 + n]
    if t == b"tEXt":
        print("[decoy] tEXt Comment:", body.split(b"\0")[1].decode())
    if t == b"eXIf":
        b32 = re.search(rb"ASCII\x00\x00\x00([A-Z2-7=]+)", body).group(1)
        print("UserComment:", b32.decode())
        print("flag:", base64.b32decode(b32).decode())
    i += 12 + n
