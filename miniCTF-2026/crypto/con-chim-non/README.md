# Con chim non

**Category:** Crypto

## Đề bài

> Con chim non trên cành hoa / Hót véo von, hót véo von / Em yêu chim, em mến chim / Vì mỗi lần chim hót em vui
>
> Format: `miniCTF{Viết_thường_ngăn_cách_nhau}`

Đề cho file `Con chim non.7z`, bên trong là 22 ảnh `1.png` … `22.png` (xem thư mục [`files/`](./files/)). Mỗi ảnh là **một con chim đậu trên dây điện**:

![22 con chim](./images/birds.png)

## Nhận diện cipher

Mỗi ký tự được thay bằng một con chim. Các con chim khác nhau ở **hướng đầu** (trái/phải), **dáng người** (tròn, cao, to) và **vị trí cái đuôi** (thẳng xuống, chéo trái, chéo phải, vểnh lên, không có đuôi). Đây là **Birds on a Wire cipher**, một kiểu thay thế đơn bảng (monoalphabetic substitution) với 26 con chim ứng với 26 chữ cái. Bảng tra có tại [dCode](https://www.dcode.fr/birds-on-a-wire-cipher) và [Geocaching Toolbox](https://www.geocachingtoolbox.com/index.php?lang=en&page=codeTables&id=birdsOnAWire).

## Giải

**Bước 1: Nhóm các ảnh giống nhau.** So sánh hash từng file thì 22 ảnh chỉ có **13 con chim khác nhau**:

```
ảnh:   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22
nhóm:  A  B  C  B  D  E  F  G  H  I  J  K  C  A  K  B  L  M  C  E  M  C
```

**Bước 2: Đối chiếu với bảng.** Một số con chim có đặc điểm rất riêng, nhận ra ngay:

| Ảnh | Đặc điểm | Chữ |
|---|---|---|
| 1 | Thân to, quay trái, đuôi chéo xuống phải | `m` |
| 5 | Thân tròn, quay phải, **không có đuôi** | `c` |
| 7 | Đuôi **vểnh lên** phía sau | `f` |
| 10 | Đuôi **rất dài** chéo xuống | `x` |

Với `m` ở đầu và `c`, `f` ở vị trí 5 và 7, 7 chữ đầu khớp đúng với **`minictf`**:

```
m  B  C  B  c  E  f   →   m i n i c t f
```

Từ đó xác định thêm được `B = i`, `C = n`, `E = t`, và các chữ này cũng khớp với hình trong bảng. 5 con chim đuôi thẳng xuống (ảnh 2, 9, 11, 12, 18) chính là 5 nguyên âm `a e i o u`, phân biệt nhau bằng hướng đầu và độ cao. Tra tiếp các con còn lại:

```
ảnh:  1 2 3 4 5 6 7 | 8 9 10 11 12 13 | 14 15 16 | 17 18 19 | 20 21 22
chữ:  m i n i c t f | b e x  u  a  n  | m  a  i  | l  o  n  | t  o  n
```

**Bước 3: Tách từ.** Bỏ tiền tố `minictf`, còn lại `bexuanmailonton`. Tách theo tiếng Việt không dấu được **"bé Xuân Mai lon ton"**. Bé Xuân Mai là ca sĩ nhí nổi tiếng với bài hát *Con chim non*, đúng với lời bài hát trong đề.

## Flag

```
miniCTF{be_xuan_mai_lon_ton}
```
