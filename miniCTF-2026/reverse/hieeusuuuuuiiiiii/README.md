# Hieeusuuuuuiiiiii

**Category:** Reverse

## Đề bài

File 7z chứa [`files/challenge`](./files/challenge) — ELF x86-64, build kèm debug info, không strip. `nm` cho thấy 2 hàm chính: `decode()` và `main()`.

## Bước 1: Bẫy trong `main()`

`main` so sánh password với `this_password_is_useless`, nhưng lưu kết quả dưới dạng **boolean** (0/1) rồi lại đem so với `0x1337`:

```asm
cmp   eax, 0x1337     ; eax là 0 hoặc 1, không bao giờ = 0x1337
sete  al
je    0x4023d1        ; nhánh in flag -> không đời nào tới được
```

Vậy nhập password đúng cũng vô ích: `[+] Flag:` là **nhánh chết**. Đây là bài **debug**: phải ép nhánh đó chạy.

Cách 1 — patch: `je` (`74 6b`) tại file offset `0x2364` đổi thành `90 90` (NOP), chạy lại là in flag:

```
[+] Debug branch reached!
[+] Flag: miniCTF{miniCTF{miniCTF{si_vo_bu_lit}}}
```

Cách 2 — gdb: break trước `cmp`, `set` biến `access = 0x1337`, `continue`.

## Bước 2: Lấy flag tĩnh

Không cần chạy vẫn lấy được flag. `decode()` dựng một buffer 39 byte trên stack từ 5 lệnh `movabs`, rồi XOR mọi byte với **`0x37`**:

```
[rbp-0x60] = 0x4c7163745e595e5a
[rbp-0x58] = 0x4c7163745e595e5a
[rbp-0x50] = 0x4c7163745e595e5a
[rbp-0x48] = 0x4255685841685e44
[rbp-0x41] = 0x4a4a4a435e5b6842   ; ghi đè 1 byte cuối khối trước
```

XOR với `0x37`. Script: [`solve.py`](./solve.py)

```
$ python solve.py
flag: miniCTF{miniCTF{miniCTF{si_vo_bu_lit}}}
```

Flag cố tình lồng 3 lớp; chuỗi chương trình in ra ở `[+] Flag:` chính là toàn bộ chuỗi này.

## Flag

```
miniCTF{miniCTF{miniCTF{si_vo_bu_lit}}}
```
