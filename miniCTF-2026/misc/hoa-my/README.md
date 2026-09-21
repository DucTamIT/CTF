# Hoạ My

**Category:** Misc

## Đề bài

Đề cho 2 file (xem thư mục [`files/`](./files/)):

- `poetry.txt`: bài thơ "Hoạ My", có bản gốc, bản sao chép lỗi và phần ghi chú.
- `bau_troi.png`: ảnh 128×128, vẽ bầu trời đêm, một chiếc lồng chim và một khối đen.

![bau_troi.png](./files/bau_troi.png)

## Bước 1: Lấy key từ bài thơ

Cuối `poetry.txt` có ghi chú:

> Bạn cần: (1) tách bản gốc ra, (2) lấy chữ đầu mỗi câu gốc,
> (3) bỏ hết dấu thanh, viết thường, ghép lại — bạn sẽ có 8 ký tự.
> Đó là chìa khoá để mở tín hiệu trong ảnh.

Bài thơ có 2 bản. **Bản gốc** nằm dưới dòng "Bản gốc — 8 câu, vẫn lục bát". **Bản sao chép** thì bị viết sai vài chỗ (`nen`, `hot`, `chanh`, `thanh`, `gap`, `khong`, thiếu dấu `?`...) để làm nhiễu. Lấy chữ đầu 8 câu của bản gốc:

| Câu | Chữ đầu |
|---|---|
| **H**oạ my, ai vẽ nên my? | h |
| **T**rông my my đẹp, hót thì my hay! | t |
| **A**i đưa my đến chốn này? | a |
| **N**ước chong gạo trắng my ngày ăn chơi. | n |
| **L**ồng son cửa đỏ thảnh thơi, | l |
| **M**y bay, my nhảy, sướng đời nhà my! | m |
| **N**ghĩ cho my cũng gặp thì! | n |
| **R**ừng xanh my có nhớ gì nữa không? | r |

```
key = "htanlmnr"
```

## Bước 2: Tìm dữ liệu giấu trong ảnh

Ảnh không có chunk lạ nào (chỉ có `IHDR`, `IDAT`, `IEND`), nên ta thử trích các bit plane. Với **LSB kênh Red**, đọc theo từng hàng từ trái sang phải, 8 bit ghép thành 1 byte, ta thấy ngay một header có nghĩa:

```
4d 79 6e 61 31 | 00 4e | 77 ff 69 6e 6c 6d 6e 72 6a 77 aa ...
 M  y  n  a  1 |  78   | payload (78 byte)
```

- `Myna1`: magic header (*myna* là tên một loài chim, hợp với chủ đề).
- `00 4e`: độ dài payload, 2 byte big-endian, bằng **78 byte**.
- Phần còn lại là payload đã bị mã hoá.

Trong payload có một chi tiết đáng chú ý: chuỗi `...nlmnr...` lộ ra gần như nguyên văn. Đó là vì plaintext ở vị trí này toàn byte `0x00` (trường thời gian của gzip header), mà `0x00 XOR key = key`. Đây là dấu hiệu payload được **XOR lặp với key**.

## Bước 3: Giải mã

XOR payload với `htanlmnr` thì kết quả bắt đầu bằng `1f 8b 08`, là magic của **gzip**. Giải nén ra flag.

Script đầy đủ: [`solve.py`](./solve.py)

```python
payload = data[7:7 + n]
plain = bytes(c ^ key[i % len(key)] for i, c in enumerate(payload))
print(gzip.decompress(plain).decode())
```

```
$ python solve.py
key: b'htanlmnr'
miniCTF{hoa_my_dong_lua_bay_xa_va_giai_ma_tieng_hot_giua_troi}
```

## Flag

```
miniCTF{hoa_my_dong_lua_bay_xa_va_giai_ma_tieng_hot_giua_troi}
```
