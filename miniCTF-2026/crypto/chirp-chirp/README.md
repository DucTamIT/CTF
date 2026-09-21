# Chirp chirp

**Category:** Crypto

## Đề bài

> Chim bay 13 vòng. Chim hót. Hót kiểu gì lạ vậy 🫪?

Đề cho file [`files/chirp.txt`](./files/chirp.txt), gồm 32 nhóm 8 bit:

```
01111010 01110110 01100001 01110110 01010000 01000111 01010011 01111011 ...
```

## Phân tích

Mô tả đề có 2 gợi ý:

- **"Chim hót... kiểu gì lạ vậy"**: tiếng hót là chuỗi `0` và `1`, tức là **binary**. Mỗi nhóm có đúng 8 bit, tương ứng 1 ký tự ASCII.
- **"Bay 13 vòng"**: xoay chữ cái 13 vị trí, tức là **ROT13**.

## Giải

**Bước 1: Binary → ASCII**

```
zvavPGS{o1a4el_pu1ec5_se0z_4s4e}
```

Kết quả đã có dạng `xxxxXXX{...}` giống format flag, nhưng các chữ cái bị dịch. Ví dụ `zvav` ứng với `mini`: `z → m` dịch đúng 13 vị trí.

**Bước 2: ROT13**

ROT13 chỉ xoay chữ cái, còn số và ký hiệu (`1`, `4`, `_`, `{`, `}`) giữ nguyên:

```
zvavPGS{o1a4el_pu1ec5_se0z_4s4e}
miniCTF{b1n4ry_ch1rp5_fr0m_4f4r}
```

Có thể làm nhanh bằng CyberChef với recipe **From Binary → ROT13**.

## Flag

```
miniCTF{b1n4ry_ch1rp5_fr0m_4f4r}
```
