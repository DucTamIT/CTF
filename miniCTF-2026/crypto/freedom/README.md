# Freedom

**Category:** Crypto

## Đề bài

> Một đêm mưa giông, bão cuốn qua khu rừng. Chiếc lồng cũ bật tung. Chú chim run rẩy, rồi dang cánh bay lên. Nhưng tự do không có nút. Trên đường đi, chim phải phá ba khóa mật mã: Knapsack, ECDSA và LFSR. Nếu phá hết, chim sẽ tìm thấy hạnh phúc. Hoặc ít nhất tìm thấy flag. Chim chỉ biết ước làm sao với được mây 💔

Web có 3 khóa phải mở lần lượt.

## Cánh 1 — Lattice Knapsack

> c = 42 = sum(a_i * x_i), a = [1, 2, 4, 8, 16, 32]. Nhập 6 bit.

`a` là các lũy thừa của 2, nên `x` chính là biểu diễn nhị phân của 42 = 32 + 8 + 2. Ghi theo thứ tự của `a`:

```
010101
```

## Cánh 2 — ECDSA Nonce Reuse

> h1=7, h2=4, s1=5, s2=2, n=23, r=11. Tìm khóa bí mật x.

Hai chữ ký dùng chung `k`, nên từ `s = k⁻¹(h + r·x) mod n` suy ra:

```
k = (h1 - h2) / (s1 - s2) = 3 / 3 = 1        (mod 23)
x = (s1·k - h1) / r      = (-2) · 11⁻¹ = (-2) · 21 = 4   (mod 23)
```

```
4
```

## Cánh 3 — PRNG Reversal (LFSR)

> LFSR 16-bit, taps 16,15,13,4. 8 output bits: 1,0,1,1,0,1,0,0. Nhập state khởi tạo.

Với LFSR dịch trái và lấy output ở MSB, 8 bit output đầu tiên chính là 8 bit cao của state ban đầu. Feedback chỉ ảnh hưởng tới các bit ra sau đó. Vì vậy 8 bit cao là `10110100`, còn 8 bit thấp không được đề cố định nên chọn bằng 0:

```
1011010000000000
```

Script kiểm tra cả 3 khóa: [`solve.py`](./solve.py)

## Flag

```
miniCTF{chim_Da_bay_e_caNh_e_CRYPt0_8ReaK_1Ree_lOn6_S47_V0_nat}
```
