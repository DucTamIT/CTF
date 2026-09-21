# Tràn Bộ Nhớ

**Category:** Reverse

## Đề bài

Service tại `103.116.52.180` (đề mang chủ đề *buffer overflow*), kèm source [`files/lyric-tran_bo_nho.py`](./files/lyric-tran_bo_nho.py). Chương trình là một trình "đọc lời bài hát".

## Phân tích

Flag được nhét vào `secret_intro` — **dòng 3** của mảng lyric, nằm *trước* điểm bắt đầu `[VERSE1]` nên bình thường không bao giờ in ra.

Dù chủ đề là buffer overflow, lỗ hổng thật là **logic bug** trong `reader()`:

1. Dòng `CROWD (...)` đọc input người dùng rồi **ghi đè lại vào mảng lyric** tại đúng dòng hiện tại:
   ```python
   crowd = input('Crowd: ')
   song_lines[lip] = 'Crowd: ' + crowd
   ```
2. `REFRAIN` nhảy về đoạn điệp khúc, khiến dòng `CROWD` đã bị đầu độc **được đọc lại**.
3. Khi đọc lại, dòng bị tách theo `;`, và bất kỳ mảnh nào khớp `RETURN [0-9]+` sẽ thành **lệnh nhảy tuỳ ý**:
   ```python
   elif re.match(r"RETURN [0-9]+", line):
       lip = int(line.split()[1])
   ```

## Khai thác

Tại prompt `Crowd:` đầu tiên, gửi:

```
x;RETURN 3
```

Dòng này được lưu thành `Crowd: x;RETURN 3`. Vòng refrain kế tiếp tách ra thành `Crowd: x` (in ra) và `RETURN 3` → `lip = 3` → nhảy đúng dòng flag và in nó ra.

Script: [`solve.py`](./solve.py)

```
$ python solve.py
flag: miniCTF{7517f1b76ce2_DUOn6_d0M1(_f94c5334-7824-4ec4-80c2-9f1246385450}
```

## Flag

```
miniCTF{7517f1b76ce2_DUOn6_d0M1(_f94c5334-7824-4ec4-80c2-9f1246385450}
```
