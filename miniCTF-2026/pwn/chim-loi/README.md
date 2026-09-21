# Chim`_loi

**Category:** Pwn

## Đề bài

ELF x86-64 (`chall`) + server `103.116.52.180:33621`.

## Phân tích

Binary **không PIE, không canary**, còn nguyên symbol. Có 3 hàm:

- `vuln()`: buffer `buf[0x50]` tại `rbp-0x50`, nhưng `read(0, buf, 0x100)` đọc tới 256 byte → **tràn stack**. Trước đó nó đặt biến local `check = 0` (tại `rbp-0x4`) và lưu địa chỉ của nó vào global `check_ptr`.
- `win()`: nếu `*check_ptr == 0xdeadbeef` thì mở `flag.txt` và in ra.

"Cửa ải" `check` chỉ là một biến nằm ngay trong vùng bị tràn, nên ghi đè luôn được.

## Khai thác

Offset tính từ đầu buffer (`rbp-0x50`):

| Offset | Ghi gì |
|---|---|
| `0x4c` (76) | `0xdeadbeef` (biến check) |
| `0x50` (80) | saved rbp |
| `0x58` (88) | return address → `win` (`0x4011e7`) |

`win` có `sub rsp,0x90` nhưng không đè lên biến `check` trước khi đọc, nên check qua và flag được in.

Script: [`solve.py`](./solve.py)

```
$ python solve.py
chim a dau ...: chua thay chim ...
miniCTF{t4i_v1_s4o_c4m_xuc_kia_qu4y_ve_0xcafebabedeadbeef}
```

## Flag

```
miniCTF{t4i_v1_s4o_c4m_xuc_kia_qu4y_ve_0xcafebabedeadbeef}
```
