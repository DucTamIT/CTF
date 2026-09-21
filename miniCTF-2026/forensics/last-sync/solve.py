import base64
import gzip
import re
import struct
from urllib.parse import parse_qs, urlparse

# Đọc pcap, lấy các HTTP GET /telemetry/sync
raw = open("files/capture.pcap", "rb").read()
i, reqs = 24, []
while i < len(raw):
    _, _, cl, _ = struct.unpack("<IIII", raw[i:i + 16])
    pkt = raw[i + 16:i + 16 + cl]
    i += 16 + cl
    m = re.search(rb"GET (/telemetry/sync\?\S+)", pkt)
    if m:
        reqs.append({k: v[0] for k, v in parse_qs(urlparse(m.group(1).decode()).query).items()})

for r in reqs:
    print(r)

# Chỉ lấy session có "total" (session 4f2a), sắp theo part chứ không theo thời gian
parts = sorted((r for r in reqs if "total" in r), key=lambda r: int(r["part"]))
b64 = "".join(r["data"] for r in parts)
print("\nbase64:", b64)

# Base64 -> gzip (magic 1f 8b) -> flag
blob = base64.b64decode(b64)
print("magic:", blob[:2].hex())
print("flag:", gzip.decompress(blob).decode())
