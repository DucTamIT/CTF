# Rem-emberMe

**Category:** Pwn

## Đề bài

`player.zip` = `chall` (PIE, stripped) + `libc.so.6` (GLIBC 2.39). Bảo vệ đầy đủ: **Full RELRO + canary + NX + PIE**. Server `103.116.52.180`. Giao diện menu theo chủ đề Re:Zero, 6 lựa chọn.

## Bug 1 — Format string (menu 4 "Cor Leonis")

Menu 4 đọc input rồi gọi `printf(buf, "Natsuki Subaru", puts_libc, "Pleiades Watchtower")`. Có validator: `strlen ≤ 7` và chỉ cho `%d`/`%i` cùng các ký tự `hljztL * $`. Vẫn đủ để dùng `%N$lld` đọc tham số theo vị trí:

| Format | Rò rỉ |
|---|---|
| `%2$lld` | tham số rdx = địa chỉ `puts` của libc → **libc base** |
| `%35$lld` | **stack canary** |

Menu 4 chỉ dùng được **2 lần** (đúng hint "the red threads snap one by one"), vừa đủ 2 leak.

## Bug 2 — Length mismatch (menu 5 "Book of the Dead")

Kích thước nhập vào bị **cắt còn 1 byte** để kiểm tra (`n & 0xff ∈ [1, 0x80]`), nhưng `read_n(buf, n)` lại dùng **full n 32-bit**. Buffer là `rbp-0x90`, canary tại `rbp-0x8` → khoảng cách `0x88`.

Chọn `n = 0x180`: byte thấp `0x80` qua được check, nhưng đọc thẳng **384 byte** vào buffer `0x88` → tràn qua canary + saved rbp + return address.

## Chain

Có libc base + canary nên ghép ROP bằng gadget libc:

```
'A'*0x88 + canary + saved_rbp + [ ret ; pop rdi ; "/bin/sh" ; system ]
```

- `ret` để căn stack 16 byte (nếu thiếu, `system` chết ở `movaps`).
- **Phải gửi đủ 384 byte** (pad bằng `\x90`), nếu không `read_n` block chờ đủ số byte đã khai.

`system("/bin/sh")` → shell dưới user `d1nhdwc` → `cat flag.txt`.

Script: [`solve.py`](./solve.py) (dùng `libc.so.6` trong `files/`)

## Flag

```
miniCTF{R3mu_w4_5h1nj1t3m45u_d4tt3...R3mu_w4_5ub4ru-kun_w0_415h1t3m45u...(T.T)}
```
