# Strange Photo

**Category:** Forensics

## Đề bài

> đang bay trên trời chú lỡ va vào một tấm ảnh nhưng bức ảnh này có gì đó hơi lạ có phải không

File đề: [`files/image.jpeg`](./files/image.jpeg). File này không mở được: `file` báo là `data`, còn `exiftool` báo `File format error`.

## Bước 1: Sửa header

Xem hex thì thấy đây là **PNG** (có chunk `IHDR`), nhưng 8 byte signature đã bị xoá mất các byte ở vị trí lẻ:

```
thực tế: 89 00 4e 00 0d 00 1a 00
đúng:    89 50 4e 47 0d 0a 1a 0a
```

Các chunk phía sau (`IHDR`, `sRGB`, `gAMA`, `pHYs`, `IDAT`, `IEND`) còn nguyên. Sửa lại signature là ảnh mở được bình thường.

## Bước 2: Dữ liệu sau IEND

Sau chunk `IEND` còn **420 byte thừa**, gồm 46 nhóm 8 ký tự chỉ có `0` và `2`:

```
02202202 02202002 02202220 02202002 ...
```

Đây là binary với `2` thay cho `1`. Mỗi nhóm là một ký tự ASCII, ví dụ `02202202` → `01101101` → `m`.

Script: [`solve.py`](./solve.py)

```
$ python solve.py
header: 89 00 4e 00 0d 00 1a 00
trailer: 02202202 02202002 02202220 02202002 ...
flag: miniCTF{chi_l4_m07_buc_4nh_th0i_co_phai_kh0n;}
```

## Flag

```
miniCTF{chi_l4_m07_buc_4nh_th0i_co_phai_kh0n;}
```
