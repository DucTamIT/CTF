#!/usr/bin/env python3
"""
The Voice 2026 — DeepSound 2.3 (`DSC2`) extractor + KDF verifier.

    python3 solve.py --selftest
    python3 solve.py --header "Con chim non.wav"
    python3 solve.py --check <password> "Con chim non.wav"
    python3 solve.py --extract <password> "Con chim non.wav" [outdir]

DeepSound 2.3 key derivation (reverse-engineered from
`Jospin.DeepSound.Steganography.Fragile.Coder::set_KeyUnicode` in Utils.dll):

    key      = SHA256( UTF-16LE(password) )
    c0       = AES-256_key( 00 * 16 )
    c1       = AES-256_key( key[16:32] ^ c0 )
    c2       = AES-256_key( 0x10 * 16 ^ c1 )          # PKCS#7 final block
    keycheck = SHA1( c0 || c1 || c2 )                 # 20 bytes, stored in header

Payload: AES-256-CBC, key as above, IV = key[:16], starting at the first byte
after the 104-byte header region.

Dependencies: `pycryptodome` for the AES paths; the header parse and --selftest
run on the standard library alone.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys

MAGIC_DSC2 = b"DSC2"
MAGIC_DSCF = b"DSCF"

# ---------------------------------------------------------------- KDF

def _aes256_encrypt_block(key: bytes, block: bytes) -> bytes:
    """Single AES-256 block encryption. Prefers pycryptodome, falls back to a
    pure-python implementation so --selftest works without dependencies."""
    try:
        from Crypto.Cipher import AES
        return AES.new(key, AES.MODE_ECB).encrypt(block)
    except ImportError:
        return _aes256_encrypt_block_py(key, block)


_SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16"
)


def _xtime(x: int) -> int:
    return ((x << 1) ^ 0x1B) & 0xFF if x & 0x80 else (x << 1) & 0xFF


def _expand_key(key: bytes) -> list:
    rk = [int.from_bytes(key[i * 4:i * 4 + 4], "big") for i in range(8)]
    for i in range(8, 60):
        t = rk[i - 1]
        if i % 8 == 0:
            t = ((t << 8) | (t >> 24)) & 0xFFFFFFFF
            t = int.from_bytes(bytes(_SBOX[(t >> s) & 0xFF] for s in (24, 16, 8, 0)), "big")
            t ^= (1 << (i // 8 - 1 + 24))
        elif i % 8 == 4:
            t = int.from_bytes(bytes(_SBOX[(t >> s) & 0xFF] for s in (24, 16, 8, 0)), "big")
        rk.append(rk[i - 8] ^ t)
    return rk


def _aes256_encrypt_block_py(key: bytes, block: bytes) -> bytes:
    rk = _expand_key(key)
    s = list(block)
    for r in range(15):
        if r > 0:
            s = [_SBOX[b] for b in s]
            t = s[:]
            for c in range(4):
                for row in range(4):
                    t[c * 4 + row] = s[((c + row) % 4) * 4 + row]
            s = t
        if 0 < r < 14:
            for c in range(4):
                a = s[c * 4:c * 4 + 4]
                s[c * 4 + 0] = _xtime(a[0]) ^ _xtime(a[1]) ^ a[1] ^ a[2] ^ a[3]
                s[c * 4 + 1] = a[0] ^ _xtime(a[1]) ^ _xtime(a[2]) ^ a[2] ^ a[3]
                s[c * 4 + 2] = a[0] ^ a[1] ^ _xtime(a[2]) ^ _xtime(a[3]) ^ a[3]
                s[c * 4 + 3] = _xtime(a[0]) ^ a[0] ^ a[1] ^ a[2] ^ _xtime(a[3])
        k = rk[r * 4:r * 4 + 4]
        for c in range(4):
            w = k[c]
            s[c * 4 + 0] ^= (w >> 24) & 0xFF
            s[c * 4 + 1] ^= (w >> 16) & 0xFF
            s[c * 4 + 2] ^= (w >> 8) & 0xFF
            s[c * 4 + 3] ^= w & 0xFF
    return bytes(s)


def derive(password: str) -> bytes:
    """SHA256(UTF-16LE(password)) — the AES-256 key."""
    return hashlib.sha256(password.encode("utf-16-le")).digest()


def keycheck_dsc2(key: bytes) -> bytes:
    """20-byte keycheck for DeepSound 2.3 (`DSC2`)."""
    c0 = _aes256_encrypt_block(key, b"\x00" * 16)
    c1 = _aes256_encrypt_block(key, bytes(a ^ b for a, b in zip(key[16:32], c0)))
    c2 = _aes256_encrypt_block(key, bytes(0x10 ^ b for b in c1))
    return hashlib.sha1(c0 + c1 + c2).digest()


def keycheck_dscf(password: str) -> bytes:
    """Legacy DeepSound 2.0 (`DSCF`): SHA1(password null-padded to 32)."""
    return hashlib.sha1(password.encode()[:32].ljust(32, b"\x00")).digest()


# ---------------------------------------------------------------- container

def find_data_chunk(buf: bytes) -> int:
    """Offset of the first audio byte in the RIFF `data` chunk."""
    i = buf.find(b"data")
    while i != -1:
        size = struct.unpack_from("<I", buf, i + 4)[0]
        if size > 1000 and 8 + i + size <= len(buf) + 64:
            return i + 8
        i = buf.find(b"data", i + 1)
    raise SystemExit("could not locate the WAV data chunk")


def parse_header(raw: bytes, base: int) -> dict:
    """26 decoded header bytes, taken from the low nibble of every other byte."""
    h = raw[base:base + 104]
    dec = bytes(((h[i] & 0x0F) << 4) | (h[i + 2] & 0x0F) for i in range(0, 104, 4))
    return {
        "magic": dec[:4],
        "mode": dec[4],
        "encrypted": dec[5],
        "keycheck": dec[6:26],
    }


def decode(buf: bytes, mode: int) -> bytes:
    """DeepSound payload decode.

    mode 8 (high) : 2 bits from bytes 0,2,4,6 of every 8-byte group
    mode 4 (normal): one nibble from bytes 0,2 of every 4-byte group
    mode 2 (low)  : whole low byte at even offsets
    """
    out = bytearray()
    if mode == 8:
        for i in range(0, len(buf) - 7, 8):
            out.append(((buf[i] & 3) << 6) | ((buf[i + 2] & 3) << 4)
                       | ((buf[i + 4] & 3) << 2) | (buf[i + 6] & 3))
    elif mode == 4:
        for i in range(0, len(buf) - 3, 4):
            out.append(((buf[i] & 0x0F) << 4) | (buf[i + 2] & 0x0F))
    elif mode == 2:
        for i in range(0, len(buf) - 1, 2):
            out.append(buf[i])
    else:
        raise SystemExit(f"unsupported mode {mode}")
    return bytes(out)


# ---------------------------------------------------------------- commands

SELFTEST = [
    ("test", "5af80536d41e826be11da7317f250ffaaa0eaf8b"),
    ("gain", "35a42fb91ff63d3bd4b4f318666f252c5d398b4f"),
    ("", "ccb7867e119a42b48fa97b19fb15634fd16e226e"),
    ("hát bé", "5b786f06b42bb9fc452f1c1cf8fb34e9f2a1bc15"),
]


def cmd_selftest() -> int:
    ok = True
    print("KDF self-test (must all be OK):")
    for pw, want in SELFTEST:
        got = keycheck_dsc2(derive(pw)).hex()
        good = got == want
        ok &= good
        print(f"  {'OK ' if good else 'FAIL'}  {pw!r:12} {got}")
        if not good:
            print(f"        expected {want}")
    print("ALL TESTS PASSED" if ok else "SOME TESTS FAILED")
    return 0 if ok else 1


def cmd_header(wav: str) -> int:
    raw = open(wav, "rb").read()
    base = find_data_chunk(raw)
    h = parse_header(raw, base)
    print(f"file       : {wav}  ({len(raw):,} bytes)")
    print(f"data chunk : offset {base}  ->  header at {base}, payload at {base + 104}")
    print(f"magic      : {h['magic']!r}")
    print(f"mode       : {h['mode']}")
    print(f"encrypted  : {h['encrypted']}")
    print(f"keycheck   : {h['keycheck'].hex()}")
    print(f"payload cap: {(len(raw) - base - 104) // h['mode']:,} bytes")
    return 0


def _decrypt_payload(raw: bytes, base: int, mode: int, key: bytes):
    from Crypto.Cipher import AES
    blob = decode(raw[base + 104:], mode)
    return AES.new(key, AES.MODE_CBC, key[:16]).decrypt(blob), blob


def cmd_check(pw: str, wav: str) -> int:
    raw = open(wav, "rb").read()
    base = find_data_chunk(raw)
    h = parse_header(raw, base)
    key = derive(pw)
    kc = keycheck_dsc2(key) if h["magic"] == MAGIC_DSC2 else keycheck_dscf(pw)
    print(f"key        : {key.hex()}")
    print(f"keycheck   : {kc.hex()}")
    if kc != h["keycheck"]:
        print("password   : NO MATCH")
        return 2
    print("password   : MATCH")
    dec, _ = _decrypt_payload(raw, base, h["mode"], key)
    print(f"first bytes: {dec[:64]!r}")
    return 0


def cmd_extract(pw: str, wav: str, outdir: str) -> int:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad

    raw = open(wav, "rb").read()
    base = find_data_chunk(raw)
    h = parse_header(raw, base)
    key = derive(pw)
    if keycheck_dsc2(key) != h["keycheck"]:
        print("password does NOT match this container")
        return 2
    mode = h["mode"]
    os.makedirs(outdir, exist_ok=True)

    pos = base + 104
    n = 0
    while True:
        block = decode(raw[pos:pos + 32 * mode], mode)
        if len(block) < 32:
            break
        info = AES.new(key, AES.MODE_CBC, key[:16]).decrypt(block)
        if info[:4] != b"DSSF":
            if n == 0:
                blob = decode(raw[pos:], mode)
                dec = AES.new(key, AES.MODE_CBC, key[:16]).decrypt(blob)
                dest = os.path.join(outdir, "payload.bin")
                open(dest, "wb").write(dec)
                print(f"no DSSF marker; wrote raw decrypted payload -> {dest}")
                return 0
            break
        name = info[4:24].decode("utf-8", "replace").replace("?", "X")
        # the 20-byte name field is NUL-padded; strip NULs before touching the fs
        name = name.rstrip("\x00").strip() or f"file{n}"
        size = struct.unpack(">I", info[24:28])[0]
        pos += 32 * mode
        data = AES.new(key, AES.MODE_CBC, key[:16]).decrypt(
            decode(raw[pos:pos + size * mode], mode))
        try:
            data = unpad(data, 16)
        except Exception:
            data = data[:size]
        dest = os.path.join(outdir, os.path.basename(name))
        open(dest, "wb").write(data)
        print(f"extracted  : {dest}  ({len(data):,} bytes)")
        n += 1
        pos += size * mode
    print(f"done: {n} file(s) in {outdir}/")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="verify the KDF against known vectors")
    ap.add_argument("--header", metavar="WAV", help="parse and print the DeepSound header")
    ap.add_argument("--check", nargs=2, metavar=("PASSWORD", "WAV"), help="test a password")
    ap.add_argument("--extract", nargs=3, metavar=("PASSWORD", "WAV", "OUTDIR"),
                    help="decrypt and extract embedded files")
    a = ap.parse_args()
    if a.selftest:
        return cmd_selftest()
    if a.header:
        return cmd_header(a.header)
    if a.check:
        return cmd_check(*a.check)
    if a.extract:
        return cmd_extract(*a.extract)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
