# Black Crow's Whitening Problem

**Category:** Reverse

## Đề bài

File đề: [`files/Black_Crow.exe`](./files/Black_Crow.exe)

## Bước 1: Sửa header

File không chạy được trên Windows (*"not a valid application"*), `file` báo là `data`. Xem hex thì thấy 2 byte đầu là `ME` thay vì **`MZ`**, magic của file PE:

```
00000000: 4d45 9000 0300 ...   ME..
```

Sửa lại thành `4D 5A` là thành file PE32+ x86-64 bình thường.

## Bước 2: Phân tích

Chạy thử:

```
==========================================
          BLACK CROW'S PROBLEM
==========================================
The crow wants to become a swan.
How many whitening baths does it need?
>
```

Mở trong IDA/Ghidra (binary còn nguyên symbol). `main` đọc một số `n`, rồi so sánh `calculate(n) == get_target()`. Nếu bằng thì gọi `print_flag()`, còn sai thì in câu trêu:

```c
uint32_t calculate(uint32_t x) {
    x ^= 0x5a5a;
    x += 0x1337;
    x *= 7;          // shl eax,3 ; sub eax,edx
    x -= 0x2468;
    x ^= 0x1f2e3d;
    return x;
}
// get_target() trả về 0xcacdb
```

## Bước 3: Đảo ngược

Mọi phép trong `calculate` đều đảo được: XOR đảo bằng chính nó, cộng/trừ thì đảo dấu, còn nhân 7 thì nhân với nghịch đảo của 7 mod 2³². Làm ngược từ `0xcacdb`:

```
0xcacdb ^ 0x1f2e3d → + 0x2468 → × 7⁻¹ → − 0x1337 → ^ 0x5a5a = 188881
```

Script: [`solve.py`](./solve.py)

## Bước 4: Lấy flag

```
How many whitening baths does it need?
> 188881
Congratulations minictf{y0u_4r3_3v3n_f41r3r_7h4n_n60c_7r1nh}
```

## Flag

```
minictf{y0u_4r3_3v3n_f41r3r_7h4n_n60c_7r1nh}
```
