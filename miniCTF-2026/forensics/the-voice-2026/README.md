# The Voice 2026

**Category:** Forensics / Steganography

## Đề bài

> Hát bé thế chả nghe thấy gì?

Hints:
1. `rockyou.txt - sản phẩm không mong muốn của ông Tokuda`
2. `Hãy thử nghiên cứu về âm thanh thật sâu vào, I mean DeepSound (")>`
3. `deepsound newest ver`
4. `miniCTF{}`

File đề: `Con chim non.wav` — 129,003,502 bytes.

**Trạng thái:** chưa giải được. Đã reverse-engineer xong format và KDF của DeepSound 2.3, dựng
xong tool bóc tách, nhưng **chưa tìm ra password** nên chưa lấy được flag. Phần dưới ghi lại
toàn bộ những gì đã làm được và những gì còn mở.

> *Status: unsolved. The DeepSound 2.3 format and KDF are fully reverse-engineered and the
> extractor is built and tested, but the password was never recovered, so the flag is not in
> this write-up. Everything below documents how far the analysis got.*

## Tổng quan

| Bước | Kết quả |
|---|---|
| Container | DeepSound **`DSC2`** ("data format v2 / 2024"), header ở offset **46** |
| Header (26 byte) | magic `DSC2` · mode `8` (high) · encrypted `1` · keycheck `c3891fa8…45f6` |
| KDF | `SHA256(UTF-16LE(pw))` → AES-256-CBC 3 block → `SHA1` — đã verify |
| Payload | offset **150**, 2 bit/sample, ~16.1 MB ciphertext AES-256-CBC |
| Password | ❌ chưa tìm ra sau ~2.4e12 candidate |

Tooling và ghi chú đầy đủ nằm ở repo riêng:
[**DucTamIT/dsc2-audio-container-analysis**](https://github.com/DucTamIT/dsc2-audio-container-analysis)
(private) — chứa format notes, verifier, GPU cracker và wordlist.

## Bước 1: File không có gì ngoài một lớp DeepSound

`Con chim non.wav`: RIFF/WAVE, PCM 16-bit stereo 44.1 kHz, dài 731.31 s (~12 ph 11 s).

| Hash | Giá trị |
|---|---|
| MD5 | `c5579bdcce8a67757b644ea7969cad3c` |
| SHA-256 | `19c88fc8b94684e773382ee69bdb198e0ee9bff18013007fb323f4b3945fe22d` |

Trước khi động vào DeepSound, đã loại bỏ toàn bộ các kênh giấu tin thông thường — **đã chạy
thật trên file này**, không cần lặp lại:

- **Spectrogram**: cả file + 148 tile (74 × 10 s full mix, 74 × 10 s kênh **L−R**), lọc băng
  5–12 kHz có khử steady-tone, render noise-floor, phase và instantaneous-frequency, zoom
  intro (0–2 s) và outro (729–731.3 s). Không có glyph, QR hay text.
- **Bit plane**: bit 0–3 của L/R, cả hai thứ tự bit, stride 1/2/4, mixed-bit liên kênh —
  không ra text; render dạng *tín hiệu* thì là white noise phẳng.
- **Audio**: không tiếng nói (Whisper small/medium, cả file + 73 cửa sổ 10 s + 20 đoạn im lặng
  nhất được amplify + audio đảo + speed 2×/4×); không SSTV (pulse 1200 Hz không đều ~1.5 s,
  SSTV cần 0.12–0.15 s); không DTMF; không Morse; không UART; không mã nhị phân theo waveform;
  không mã rhythm/onset; không raster analog.
- **Literal text**: `strings` (ASCII + UTF-16LE), UTF-8 multibyte, low-byte/high-byte stream,
  và decode nibble kiểu DeepSound ở **cả 4 phase** — chuỗi đọc được duy nhất trong toàn file
  chính là **26-byte header DeepSound**.
- **Container**: RIFF khớp hoàn toàn (không trailing data, không chunk lạ); 7z không có
  appended data và không comment.

Vậy flag nằm sau đúng một password.

## Bước 2: DeepSound 2.3 dùng `DSC2`, không phải `DSCF`

Tool CTF phổ biến (`deepsound2john.py`, Hashcat `-m 29700`, John `dynamic_1529`) đều nhắm
**DeepSound 2.0 / `DSCF`**, nên chạy vào container này là fail. Hint 3 (`deepsound newest ver`)
chính là để chỉ ra điều đó.

| | Legacy 2.0 (`DSCF`) | **2.3 (`DSC2`)** |
|---|---|---|
| Magic | `DSCF` | **`DSC2`** |
| KDF input | ASCII | **UTF-16LE** |
| Hash | SHA-1 | **SHA-256** |
| Cipher | AES-128-CBC | **AES-256-CBC** |
| Keycheck | `SHA1(password null-pad 32)` | **3 block AES-256-CBC liên hoàn + SHA-1** |

### Header

DeepSound giấu header vào **low nibble của mỗi byte cách một byte**, bắt đầu từ byte đầu của
chunk `data`:

```
out[i] = (buf[4i] & 0x0F) << 4 | (buf[4i+2] & 0x0F)
```

Lấy 104 byte carrier từ offset 46 → 26 byte header:

```
0x00-0x03 : "DSC2"                                    (magic)
0x04      : 0x08                                      (mode 8 = high, 2 bit/sample)
0x05      : 0x01                                      (encrypted)
0x06-0x19 : c3891fa82c0a842db941d5d4656b35f69ecd45f6  (keycheck 20 byte)
```

### Payload

Bắt đầu ở raw offset **150** = `46 + 104`. Mode 8 lấy 2 bit từ byte 0, 2, 4, 6 của mỗi nhóm
8 byte:

```
mode 8 : ((buf[i]&3)<<6) | ((buf[i+2]&3)<<4) | ((buf[i+4]&3)<<2) | (buf[i+6]&3)
mode 4 : ((buf[i]&0x0F)<<4) | (buf[i+2]&0x0F)
mode 2 : buf[i]
```

Sức chứa ~16,125,437 byte. Đây là **AES-256-CBC ciphertext**, và IV **chính là 16 byte đầu
của key**.

## Bước 3: Reverse-engineer KDF

Hàm `Jospin.DeepSound.Steganography.Fragile.Coder::set_KeyUnicode` (verify trên `Utils.dll`
của cả DeepSound 2.2 **và** 2.3):

```
key      = SHA256( UTF-16LE(password) )

IV       = key[0:16]
plain    = key[0:16] || key[16:32] || 16 * 0x10      # PKCS#7 padding
c0       = AES-256_key( key[0:16]  XOR IV  ) = AES-256_key( 0^16 )
c1       = AES-256_key( key[16:32] XOR c0  )
c2       = AES-256_key( 0x10^16    XOR c1  )

keycheck = SHA1( c0 || c1 || c2 )                    # 20 byte, lưu trong header
```

Chú ý: **không salt, không iteration** — chỉ một lần SHA-256. Đây là lý do brute-force khả thi.

### Test vectors (đã verify)

| Password | UTF-16LE | Keycheck SHA-1 |
|---|---|---|
| `test` | `7400650073007400` | `5af80536d41e826be11da7317f250ffaaa0eaf8b` |
| `gain` | `6700610069006e00` | `35a42fb91ff63d3bd4b4f318666f252c5d398b4f` |
| `""` | *(rỗng)* | `ccb7867e119a42b48fa97b19fb15634fd16e226e` |
| `hát bé` | `6800e100740020006200e900` | `5b786f06b42bb9fc452f1c1cf8fb34e9f2a1bc15` |

```bash
python solve.py --selftest      # -> ALL TESTS PASSED
```

## Bước 4: GPU cracker

Hashcat không hỗ trợ `DSC2` (`-m 29700` chỉ có `DSCF`), và bản C CPU chỉ đạt ~1.1 M c/s, nên
phải viết cracker OpenCL riêng. Kernel `ds_check_word_fast` ép cả chuỗi mật mã vào register GPU:

1. Chuyển UTF-16LE in-place, tối đa 54 ký tự → gói vừa **một** block SHA-256, không branching.
2. SHA-256 nén 1 block, 64 round unrolled → key 256-bit trong register.
3. AES-256 key expansion 14 round (60 subkey) trong register.
4. AES-CBC 3 block bằng T-box (`te0`…`te3`) → `c0, c1, c2`.
5. SHA-1 nén 1 block, 80 round unrolled, trên 48 byte ciphertext.
6. **Early termination**: so byte 0 của target hash, loại ngay trước khi ghi global memory.

Trên **RTX 3060 Laptop**: ~**35 M c/s**. Duyệt hết `rockyou.txt` (14.3 M) mất ~0.42 s compute
(~5.3 s cả I/O).

Sanity check trước khi chạy — phải in MATCH:

```bash
ds_gpu.exe --hash 5af80536d41e826be11da7317f250ffaaa0eaf8b --printable 4
```

## Bước 5: Không gian đã dò — chưa ra

Target: `c3891fa82c0a842db941d5d4656b35f69ecd45f6`

| Không gian | Candidate | Kết quả |
|---|---|---|
| printable ASCII `^1..6` | 7.35e11 | ❌ |
| `[a-z0-9]^1..6` | 2.24e9 | ❌ |
| `[a-z]^7` | 8.03e9 | ❌ |
| `[a-zA-Z0-9_{}]^4..5` | 1.18e9 | ❌ |
| Tiếng Việt 2 từ (dict 77k) | 5.94e9 ×2 | ❌ |
| Tiếng Việt 3 từ (3000 phổ biến) | 2.7e10 ×2 | ❌ |
| rockyou + 287 M rules, dict Việt + affix, wordlist breach, từ điển macOS, teencode, TELEX/VNI/VIQR, idiom, metadata | ~1.5e9 | ❌ |
| John `--rules` + format `deepsound2` | 1.1 M c/s | ❌ |
| Các biến thể flag `miniCTF{…}` | ~473 M | ❌ |
| `miniCTF{[a-z0-9]^1..7}` | 78.4e9 | ❌ |

**Suy ra được:** password **≥ 7 ký tự** nếu là printable ASCII; **≥ 7** nếu chỉ lowercase hoặc
alnum; **≥ 6** nếu thuộc `[a-zA-Z0-9_{}]`.

### Vì sao hint 1 đáng nghi

Hint 1 nói `rockyou.txt - sản phẩm không mong muốn của ông Tokuda` (Lance Tokuda — tác giả
`rockyou.txt`). Nếu password **nằm trong rockyou** thì đã ra ở lượt đầu. Nên hint này khả năng
cao chỉ vào **chủ đề** (bài hát thiếu nhi / tuổi thơ), hoặc là misdirection — password có thể là
biến thể của một từ trong rockyou chứ không phải chính từ đó.

### Hướng còn mở

1. **Mask ngắn chưa phủ hết**: `[a-z]^8` (2.1e11, ~9 min), `[a-z0-9]^7` (7.8e10, ~3 min).
2. **Lời bài hát "Con chim non"** — khoảng trống lớn nhất. Mới thử `conchimnon`, `xuanmai` và
   dict tiếng Việt tổng quát, **chưa dùng lời hát** làm nguồn: từng câu, từng từ, có/không dấu,
   viết liền, viết hoa, thêm năm.
3. **Tổ hợp từ tiếng Việt** có dấu/không dấu ghép với `miniCTF{}`.
4. **Từ chính challenge**: `thevoice`, `the_voice`, `betuoi`…

## Bước 6: Tool bóc tách — sẵn sàng chạy

[`solve.py`](./solve.py) làm hết: parse header, verify KDF, decode payload, AES-CBC decrypt,
parse block `DSSF`, ghi file ra.

```bash
python solve.py --selftest                              # verify KDF, không cần file đề
python solve.py --header "Con chim non.wav"             # in header
python solve.py --check "PASSWORD" "Con chim non.wav"   # thử 1 password
python solve.py --extract "PASSWORD" "Con chim non.wav" deepsound_out/
```

Cấu trúc block file-info:

```
0x00-0x03 : "DSSF"
0x04-0x17 : filename (UTF-8, NUL-padded, 20 byte)
0x18-0x1B : size (big-endian uint32, = số byte ciphertext cần đọc)
```

### Đã verify tới đâu

| Kiểm tra | Kết quả |
|---|---|
| KDF vs 4 test vectors | ✅ `ALL TESTS PASSED` (chạy bằng stdlib thuần) |
| Round-trip toàn pipeline trên container `DSC2` tổng hợp | ✅ `ROUND-TRIP OK` |
| Password sai bị từ chối | ✅ exit code 2, `NO MATCH` |
| Chạy trên `Con chim non.wav` thật | ❌ chưa làm được — file 129 MB không có trong repo |

[`_selftest_roundtrip.py`](./_selftest_roundtrip.py) tự dựng một container `DSC2` hợp lệ rồi
chạy `--header`, `--check` (đúng + sai), `--extract` qua subprocess, và so file bóc ra với bản
gốc. Nó bắt được **3 bug** trong lần viết đầu:

1. `find_data_chunk` bỏ qua chunk `data` nhỏ hơn 1000 byte.
2. Tên file 20 byte NUL-padded chưa được cắt NUL → `ValueError: embedded null character`.
3. Field `size` phải là **độ dài ciphertext** (đã pad), không phải độ dài plaintext.

## Kết luận

1. **Đừng tin tool cũ.** `deepsound2john.py` / Hashcat `-m 29700` / John `dynamic_1529` đều chỉ
   có `DSCF`. DeepSound 2.3 đổi cả magic, serialization (UTF-16LE), hash (SHA-256) và cipher
   (AES-256) — phải đọc magic rồi disassemble, không dùng lại script cũ được.
2. **KDF yếu một cách nguy hiểm.** Dùng AES-256 nhưng chỉ **một** vòng SHA-256, không salt,
   không memory-hard. GPU đạt hàng chục triệu key/giây.
3. **DeepSound không append data vào cuối file.** Nó sửa LSB của sample trong chunk `data`, giữ
   nguyên header RIFF và kích thước file — nên không phát hiện được bằng cách so file size.
4. **Bài này chưa xong.** Format và KDF thì đã sạch, tool đã sẵn sàng, nhưng password vẫn là ẩn
   số. Flag thật chưa lấy được.

## Flag

```
Chưa có — chưa tìm ra password.
```
