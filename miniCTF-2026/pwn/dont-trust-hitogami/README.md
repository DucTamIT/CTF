# d0nt_tru5t_h1t0g4m1

**Category:** Pwn

## Đề bài

Chủ đề Mushoku Tensei. ELF x86-64 PIE, stripped, server `103.116.52.180`. Bảo vệ: **Full RELRO, không canary**, và quan trọng nhất **`GNU_STACK` là RWE** (stack thực thi được). Menu 3 lựa chọn: Hitogami / Orsted / trust yourself.

## Phân tích

- **Option 1 (Hitogami):** in ra `[Hitogami's Mark Location]: <&check_val>` (địa chỉ PIE), rồi `read(buf, 0x7f)` và `printf(buf)` → **format string bug**.
- **Option 2 (Orsted):** chỉ chạy `read(buf, 0x200)` vào buffer `0x80` (tràn stack) **nếu** biến toàn cục `check_val == 0xdeadbeef`. Không canary → ghi đè thẳng return address.

`check_val` tại `0x404c`. Cả hai handler cùng layout (`buf = rbp-0x80`) và được gọi từ cùng vòng menu, nên `buf_option2 = rbp_main - 0xa0`.

## Khai thác

**1. Leak.** Option 1 in sẵn `&check_val`. Dùng `%22$p` để leak `rbp` của `main`, từ đó tính địa chỉ buffer của option 2 (`rbp_main - 0xa0`). Buffer input nằm ở arg 6 (offset 0).

**2. Ghi cổng `check_val = 0xdeadbeef`.** Dùng format string với 2 lần `%hn`, địa chỉ đặt ở offset 88/96 (= arg 17/18):

```
%48879c%17$hn%8126c%18$hn  + pad(88) + p64(&check_val) + p64(&check_val+2)
```

`0xbeef = 48879`, cộng thêm `8126` thành `0xdead`. Cả payload ≤ `0x7f`.

**3. Shellcode.** Vào option 2, `read(0x200)` vào buffer `0x80`. Vì stack RWE, đặt shellcode `execve("/bin//sh")` ở đầu buffer, pad tới `0x88`, ghi return address = địa chỉ buffer:

```
shellcode + '\x90'*pad + p64(buf)
```

Return về buffer → thực thi shellcode → shell (user `d0nt_tru5t_h1t0g4m1`) → `cat flag.txt`.

Script: [`solve.py`](./solve.py)

## Flag

```
miniCTF{r0xy_w4_s41k0_n0_w41fu_d4k4r4_z3tt41}
```
