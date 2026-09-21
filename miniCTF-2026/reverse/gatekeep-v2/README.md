# GateKeep v2

**Category:** Reverse

## Đề bài

File đề: [`files/chall`](./files/chall) — ELF x86-64, không strip. Đây là bản nâng cấp của GateKeep v1, thêm một lớp bẫy.

## Bước 1: Cổng ngoài

`main` nhận input 5 chữ số (10000–99999), biến thành key 5 byte, rồi chọn `payload = payloads[n % 6]` và giải mã:

```
plain[i] = payload[i] ^ key[i%5] ^ ((i*7 + 0x23) & 0xff)
```

Ghi ra `out.bin`. Có 6 payload; **5 payload** giải ra flag mồi:

| n % 6 | Flag mồi |
|---|---|
| 0 | `miniCTF{R34l_0r_F4k3}` |
| 1 | `miniCTF{M4y_b3_Rela??}` |
| 2 | `miniCTF{Trust_m3_1t'5_Re4l}` |
| 4 | `miniCTF{good_h33r'5_y0ur_f4k3_fl4g}` |
| 5 | `miniCTF{5h0ut_0ut_t0_Ch4t9pt!!!}` |

Tất cả đều là bẫy (một cái còn ghi thẳng `f4k3_fl4g`).

## Bước 2: Cổng trong

Payload còn lại (`payload_3`, dài 861 byte thay vì ~159) là payload duy nhất không ra flag ngắn. Nó tương ứng `n % 6 == 3`, ví dụ `n = 57321`. Giải mã payload này ra một **script Python ẩn** (`=== INNER MAGIC GATE v2 ===`) — đây mới là validator thật ([`files/inner_gate.py`](./files/inner_gate.py)):

```python
def check(text):
    if len(text) != 36: return False
    data = bytearray(text.encode()); data.reverse()
    for i in range(len(data)):
        data[i] ^= (0x23 + i*9) & 0xff
        data[i] = (data[i] + i*5 + 7) & 0xff
        data[i] = rol8(data[i], i%3 + 1)
    target = bytes.fromhex("ca7c92d8...9db74f")
    return data == target
```

## Bước 3: Giải ngược

`check()` gồm reverse → xor → cộng → xoay, tất cả khả nghịch. Đảo ngược từ `target`:

```
ror8 → trừ (i*5+7) → xor (0x23+i*9) → reverse
```

Script: [`solve.py`](./solve.py)

```
$ python solve.py
flag: miniCTF{5t1ll_345y_g4te_k33p_r1ght?}
```

Nhập chuỗi này vào inner gate cho `Gate opened`; flag mồi bị từ chối.

## Flag

```
miniCTF{5t1ll_345y_g4te_k33p_r1ght?}
```
