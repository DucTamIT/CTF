# Charlotte's Heart

**Category:** Reverse

## Đề bài

> Chú chim nhỏ lạc vào vương quốc đỏ PTIT... Chú quyết định mở khóa trái tim nàng bằng 1 chương trình. Flag format: `minictf{password}`

File đề: [`files/CharlotteHeart.exe`](./files/CharlotteHeart.exe) — crackme C++ (MinGW-w64), hỏi **Username** và **Password**.

## Bước 1: Giải mã chuỗi

Mọi chuỗi trong binary đều bị mã hoá, dựng lại lúc chạy bởi hàm tại `0x140001540` (mỗi byte: `rol`, XOR keystream, XOR `0xa5`, XOR ciphertext). Reimplement hàm này rồi giải hết chuỗi, ta thấy UI text và **3 decoy**:

| Chuỗi | Loại |
|---|---|
| `1_L1k3_7H47_pr1nc355` | decoy |
| `1f_1_f1nd_7h3_fL46_w1LL_5h3_n071c3_m3` | decoy |
| `[CharlotteVM DEBUG NOTE]` → `w0w_Y0u_rE4LLy_kn0W_4B0u7_r3v3r53_3n61n33r1n6` | decoy |

Nhập cả 3 chuỗi này làm password đều nhận `The princess turns away...`.

## Bước 2: Máy ảo kiểm tra password

Password được kiểm tra bằng một **VM tự chế** (8 thanh ghi, bytecode ~2000 byte tại `0x1400052e0`, opcode và operand đều bị mã hoá theo keystream sinh từ **username**). VM chạy tối đa 5000 bước rồi để lại một trạng thái thanh ghi.

Bytecode bị re-key theo username nên không brute-force được. Nhưng ta không cần giải cả VM: **điều kiện thắng** và **flag** đều chỉ phụ thuộc vào trạng thái thanh ghi đích, vốn là các hằng số cố định trong code.

## Bước 3: Đọc điều kiện thắng và sinh flag

Tại `0x1400036be`, chương trình chỉ in flag khi:

```asm
mov  edx, [r0]
mov  ebx, [r1]
rol  edx, 3
xor  edx, ebx
cmp  edx, 0xa39bc00a      ; rol(r0,3) ^ r1 == 0xa39bc00a
cmp  r0,  0x537f9c1b      ; r0 == 0x537f9c1b
```

Suy ra ngay `r1 = rol(0x537f9c1b, 3) ^ 0xa39bc00a`. Ngay sau đó (`0x14000379c`) flag được sinh ra:

```
seed = rol(r1, 7) ^ 0xc4a87c76
```

`seed` khởi tạo một PRNG (xor-mul-xor với hằng `0x9e3779b9`) sinh keystream, XOR với 55 byte tại `0x1400050c0` ra nội dung flag, bọc trong `minictf{...}`.

Flag **không phải mật khẩu** — nó được giải mã từ trạng thái đích của VM, nên chỉ cần đọc điều kiện thắng là dựng được, không cần tìm password.

Script: [`solve.py`](./solve.py)

```
$ python solve.py
flag: minictf{y0u_h4v3_0v3rc0m3_7h3_ch4LL3n63_4nd_w0n_h3r_h34r7_:3333}
```

## Flag

```
minictf{y0u_h4v3_0v3rc0m3_7h3_ch4LL3n63_4nd_w0n_h3r_h34r7_:3333}
```
