# GateKeep v1

**Category:** Reverse

## Đề bài

File đề: [`files/magic_gate_keep_v1.py`](./files/magic_gate_keep_v1.py). Chương trình hỏi một `key`, đưa qua hàm `g()` và in `Gate opened` nếu đúng.

## Phân tích

`g()` là một **state machine** với biến `p` nhảy giữa hàng chục nhánh. Nhưng mọi điều kiện rẽ nhánh đều là **hằng số** (`3*7==21`, `1<<5==32`, `q^q==0`...), không phụ thuộc input. Lần theo `p` thì luồng thực luôn cố định:

```
p=17 (biến đổi 1) → ... → p=4 (biến đổi 2) → ... → p=23 (kiểm tra)
```

Toàn bộ nhánh giữa chỉ là màn khói. Các phép biến đổi thật áp lên `b = input`:

1. **p=17:** yêu cầu `len == 30`, rồi `b = reverse(input)`, sau đó `b[i] ^= (i*11 + 0x35) & 255`.
2. **p=4:** `b[i] = rol(b[i], i%5+1)`, rồi `b[i] = (b[i] + i*7 + 13) & 255`.
3. **p=23:**
   - `c = b[::2] + b[1::2][::-1]` (tách chẵn/lẻ)
   - `c[i] ^= 0xA7` nếu `i==0`, ngược lại `^= c[i-1]` (xor-chain với plaintext trước đó)
   - so sánh `c` với hằng số `z` (30 byte).

## Giải

Mọi bước đều khả nghịch, nên đảo ngược từ `z`:

1. Đảo xor-chain: `old[0] = z[0]^0xA7`, `old[i] = z[i]^old[i-1]`.
2. Đảo tách chẵn/lẻ: `even = c[:15]`, `odd = c[15:][::-1]`.
3. Đảo cộng + xoay: `b[i] = ror(b[i] - (i*7+13), i%5+1)`.
4. Đảo xor mask, rồi đảo reverse.

Script: [`solve.py`](./solve.py)

```
$ python solve.py
flag: miniCTF{34sy_g4t3_k3ep_r1ght?}
```

Nhập lại chuỗi này vào chương trình gốc cho ra `Gate opened`.

## Flag

```
miniCTF{34sy_g4t3_k3ep_r1ght?}
```
