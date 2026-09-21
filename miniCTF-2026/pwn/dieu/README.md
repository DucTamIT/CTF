# Diệu

**Category:** Pwn

## Đề bài

Dịch vụ TCP tại `103.116.52.180:40281` (GZCTF liệt kê dưới dạng URL nhưng thực chất là raw TCP). Banner:

```
=== miniCTF Format String ===
[*] is_admin is at: 0x4c73b0
[*] is_admin = 0
Input:
```

## Phân tích

Chương trình in sẵn địa chỉ của biến `is_admin` (cố định, **non-PIE**) rồi gọi `printf(buf)` trực tiếp trên input của người dùng → **format string bug**. Cần ghi cho `is_admin` khác 0.

Gửi `%p %p %p ...` thấy input của mình xuất hiện ở **arg 6** (giá trị `0x7025...` là các byte `%p `). x86-64 dùng slot 8 byte, nên:

```
arg = 6 + offset/8
```

Để địa chỉ đích đặt trong buffer trỏ tới đúng bằng `%hhn`, nó phải nằm ở **arg 10** (byte offset 32, canh 8).

## Khai thác

Chỉ cần ghi 1 byte khác 0 vào `is_admin`, nên dùng `%hhn`:

- `%1$c` in đúng 1 ký tự → bộ đếm = 1.
- `%10$hhn` ghi giá trị đếm (1) vào **low byte** của con trỏ ở arg 10.
- Phần prefix format phải dài đúng 32 byte, rồi mới tới `p64(is_admin)`.

Lưu ý: gửi địa chỉ dưới dạng đủ 8 byte (`p64`) để slot vararg là con trỏ hợp lệ — nếu để `\n` dính ngay sau 4 byte địa chỉ thì byte cao thành `0x0a` và `%hhn` segfault.

```
payload = "%1$c%10$hhn" + "A"*21 + p64(0x4c73b0) + "\n"    # tổng 41 byte
```

Script: [`solve.py`](./solve.py) (tự parse địa chỉ từ banner)

```
[+] Welcome, admin!
miniCTF{f0rm4t_str1ng_1s_d4ng3r0us}
```

## Flag

```
miniCTF{f0rm4t_str1ng_1s_d4ng3r0us}
```
