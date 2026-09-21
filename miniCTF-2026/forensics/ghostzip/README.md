# GhostZip

**Category:** Forensics

## Đề bài

> Chú chim sẻ trở về từ vùng đất của kí ức và đã trả lại cho tôi file zip này. Có điều gì đó kì lạ với nó...

File đề: [`files/GhostOrSmth.zip`](./files/GhostOrSmth.zip)

## Bước 1: "Zip" thực chất là PNG

File không giải nén được, `file` báo là `data`. Xem hex thì thấy chunk `IHDR` ngay đầu file. Đây là **PNG** mà 8 byte signature đã bị thay bằng 7 byte rác:

```
13 45 15 67 0a 1a 0a | 00 00 00 0d 49 48 44 52 ...   (IHDR)
```

Bỏ 7 byte đầu, ghi lại `89 50 4E 47 0D 0A 1A 0A` là được ảnh PNG kích thước 2048×1365.

## Bước 2: Dữ liệu giấu trong MSB

Nhìn bit plane cao nhất (bit 7) của cả 3 kênh thì thấy nhiễu, trong khi ảnh gốc lẽ ra phải mượt, nên có dữ liệu được giấu ở đây. Đọc bit 7 theo thứ tự từng pixel `R, G, B, R, G, B, ...` (1131 hàng đầu), gom 8 bit thành 1 byte, ta được **~868 KB văn bản UTF-8**:

```
Viele Erinnerungen aus der Jugend entstehen nicht bei großen ...
```

Đó là các đoạn văn về tuổi trẻ bằng nhiều thứ tiếng (Đức, Anh, Nga, Việt, Hàn, Nhật, Trung, Tây Ban Nha, Pháp), bị xáo trộn và **lặp lại khoảng 110 lần**.

## Bước 3: Tìm đoạn bị chèn thêm

Văn bản toàn là các đoạn lặp lại, nên chữ nào được chèn thêm thì sẽ **chỉ xuất hiện đúng 1 lần**. Cách lọc: một ký tự là "lạ" nếu mọi chuỗi 16 ký tự chứa nó đều là duy nhất trong cả file. Lọc theo cách đó ra đúng 5 mảnh:

```
vrwrLCO{cd01_   (đoạn tiếng Nga)
ca3_            (đoạn tiếng Pháp)
ldj_            (đoạn tiếng Pháp)
c01_            (đoạn tiếng Đức)
m3y_ujv}        (đoạn tiếng Việt)
```

## Bước 4: ROT-9

Ghép 5 mảnh lại được `vrwrLCO{cd01_ca3_ldj_c01_m3y_ujv}`. So `vrwr` với `mini` thì mỗi chữ bị dịch đi 9, tức là **Caesar/ROT-9**. Dịch lùi 9 ra câu *"tuổi trẻ của tôi đẹp lắm"*.

Script: [`solve.py`](./solve.py)

```
$ python solve.py
header: 13 45 15 67 0a 1a 0a
image: (2048, 1365)
payload: 606094 ký tự, mở đầu: Viele Erinnerungen aus der Jugend entstehen nicht bei großen
fragments: ['vrwrLCO{cd01_', 'ca3_', 'ldj_', 'c01_', 'm3y_ujv}']
cipher: vrwrLCO{cd01_ca3_ldj_c01_m3y_ujv}
flag:   miniCTF{tu01_tr3_cua_t01_d3p_lam}
```

## Flag

```
miniCTF{tu01_tr3_cua_t01_d3p_lam}
```
