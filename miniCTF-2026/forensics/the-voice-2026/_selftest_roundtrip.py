#!/usr/bin/env python3
"""Build a synthetic DeepSound DSC2 container and round-trip it through solve.py.

Proves end-to-end that the header layout, mode-8 payload decode, and AES-256-CBC
parameters in solve.py are mutually consistent — without needing the 129 MB WAV.
"""
import hashlib
import os
import struct
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solve import derive, keycheck_dsc2, decode, find_data_chunk, parse_header  # noqa: E402

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

HERE = os.path.dirname(os.path.abspath(__file__))
PASSWORD = "conchimnon"
# 48 bytes -> 64 bytes of CBC ciphertext, i.e. exactly 4 x 16-byte blocks. The
# extractor reads size*mode carrier bytes and only trims afterwards, so the
# synthetic container must declare a size that is a multiple of 16.
FLAG = b"miniCTF{synthetic_roundtrip_check_0123456789abc}"[:48]


def build(path: str) -> None:
    key = derive(PASSWORD)
    kc = keycheck_dsc2(key)

    # file-info block: DSSF + 20-byte NUL-padded name + BE size, AES-CBC(key, iv=key[:16])
    # the size field is the number of *ciphertext* bytes the reader must consume,
    # so it is the padded (16-aligned) length, not the plaintext length.
    name = b"flag.txt" + b"\x00" * 12
    data_enc = AES.new(key, AES.MODE_CBC, key[:16]).encrypt(pad(FLAG, 16))
    info = b"DSSF" + name + struct.pack(">I", len(data_enc))
    info_enc = AES.new(key, AES.MODE_CBC, key[:16]).encrypt(pad(info, 16))

    plain_stream = info_enc + data_enc

    # header: 26 bytes -> interleaved into low nibbles of 104 carrier bytes
    hdr = b"DSC2" + bytes([8, 1]) + kc
    assert len(hdr) == 26

    carrier = bytearray()
    # header region: out[i] = (buf[4i]&0xF)<<4 | (buf[4i+2]&0xF)
    for i in range(26):
        hi, lo = (hdr[i] >> 4) & 0xF, hdr[i] & 0xF
        carrier += bytes([0x00 | hi, 0x00, 0x00 | lo, 0x00])

    # payload region, mode 8: recreate the byte pairs so decode() returns plain_stream
    for b in plain_stream:
        n0, n1, n2, n3 = (b >> 6) & 3, (b >> 4) & 3, (b >> 2) & 3, b & 3
        carrier += bytes([n0, 0xA5, n1, 0x5A, n2, 0xA5, n3, 0x5A])

    data = bytes(carrier) + b"\x00" * 4096   # pad past the >1000-byte data-chunk guard
    riff = (b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
            + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 2, 44100, 176400, 4, 16)
            + b"data" + struct.pack("<I", len(data)) + data)
    open(path, "wb").write(riff)
    print(f"built {path}: {len(riff):,} bytes")


def run(*args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "solve.py"), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    tmp = os.path.join(HERE, "_synth")
    os.makedirs(tmp, exist_ok=True)
    wav = os.path.join(tmp, "synthetic.wav")
    out = os.path.join(tmp, "out")
    build(wav)

    ok = True
    print("\n--- --header ---")
    rc, o = run("--header", wav)
    print(o.strip())
    ok &= rc == 0 and "DSC2" in o and "mode       : 8" in o

    print("--- --check with the WRONG password (must fail) ---")
    rc, o = run("--check", "wrongpassword", wav)
    print(o.strip())
    ok &= rc == 2 and "NO MATCH" in o

    print("--- --check with the correct password ---")
    rc, o = run("--check", PASSWORD, wav)
    print(o.strip())
    ok &= rc == 0 and "MATCH" in o

    print("--- --extract ---")
    rc, o = run("--extract", PASSWORD, wav, out)
    print(o.strip())
    extracted = os.path.join(out, "flag.txt")
    got = open(extracted, "rb").read() if os.path.exists(extracted) else b""
    ok &= rc == 0 and got == FLAG
    print(f"extracted file matches original flag: {got == FLAG}  ({got!r})")

    print("\n" + ("ROUND-TRIP OK" if ok else "ROUND-TRIP FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
