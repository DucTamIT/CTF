# Hidden things

**Category:** OSINT

## Đề bài

> Hoangdebongtoi, 1 member trong ISP đã giấu thứ gì đó trên ispclub.vn, hãy vào trang cá nhân của anh ấy để điều tra.

Trang cá nhân: `https://ispclub.vn/isper/hoangdebongtoi`

> ⚠️ Đây là chuỗi OSINT nhiều tầng. Write-up ghi lại toàn bộ đường đi tới thế giới Minecraft; **bước cipher cuối cùng trong Minecraft vẫn đang xử lý**.

## Tầng 1 — Zero-width steganography trong bio

Bio của profile trông bình thường nhưng chứa rất nhiều **ký tự Unicode ẩn (zero-width)** xen giữa các chữ. Lấy dữ liệu profile qua API `https://ispclub.vn/api/profile/hoangdebongtoi`, phần `bio` có 8 loại ký tự zero-width khác nhau (`U+200B/C/D`, `U+2060/2062/2063/2064`, `U+FEFF`) → mỗi ký tự mang **3 bit**. Đây là định dạng của công cụ **[StegZero](https://stegzero.com/)** (chế độ Standard).

Decode bằng đúng protocol của StegZero (header magic `A55A`, version 1, len 238, CRC khớp) cho ra thông điệp tiếng Việt:

> Chúc mừng thám tử nhí đã tìm ra tôi :> Hoangdebongtoi đã để lại 1 message nữa với 6 ký tự như sau **`7ZIs2s`**, liệu bạn có thể tìm ra ý nghĩa của chúng? Có vẻ vẫn còn thiếu gì đó thì phải.

Bio cũng có gợi ý GitHub: username = `hoangdebongtoi` + ngày sinh (DDMM).

## Tầng 2 — GitHub

Bio nói ngày sinh ghép vào username. Với ngày sinh **26/4** → GitHub là [`hoangdebongtoi2604`](https://github.com/hoangdebongtoi2604).

![Ngày sinh 26/4](./images/birthday_april26.png)

Profile công khai chuỗi `6677wwutsubb!@#` (khoá cho các bước sau):

![Phrase trên GitHub](./images/github_phrase.png)

Trong repo `Does-this-repo-have-any-value-`, commit **`d3810eb`** (message "Nothing") thêm dòng **`AeKiE`**:

![Commit AeKiE](./images/commit_aekie.png)

## Tầng 3 — YouTube

Ghép 2 mảnh: `7ZIs2s` (bio) + `AeKiE` (commit) = **`7ZIs2sAeKiE`** — đúng **11 ký tự = YouTube video ID**:

`https://youtu.be/7ZIs2sAeKiE` ("The Amazing Spider-Man 2 ringtone")

Comment của `@vulam8576` chứa một chuỗi Base64:

![YouTube comment](./images/youtube_comment.png)

```
NTEuMjA1MDU5Miw1MS4zNzAwNjg4  →  51.2050592,51.3700688
```

Đây là **toạ độ địa lý**.

## Tầng 4 — OpenStreetMap

Tra toạ độ `51.2050592, 51.3700688` (gần Oral, Kazakhstan) trên OpenStreetMap, tìm thấy một **note** chứa link Google Drive:

![OSM note](./images/osm_note.png)

Folder Drive: `1uRfXnKeXvsYLQnIoVCxKwwH1X-0GomtL`

## Tầng 5 — Google Drive → Minecraft

Folder Drive chứa:

- `1.21.11.zip` — một **world Minecraft** (tên `Osint`, phiên bản 1.21.11).
- `Xin chào thiên tày osint.docx` — hướng dẫn: tải world vào launcher, chọn bản 1.21.11, và tìm thứ được giấu bên trong.

## Chuỗi OSINT tổng quát

```
ISP profile (bio)
  └─ StegZero zero-width  →  7ZIs2s
      └─ GitHub hoangdebongtoi2604, commit d3810eb  →  AeKiE
          └─ 7ZIs2sAeKiE  →  YouTube
              └─ comment @vulam8576 (Base64)  →  toạ độ
                  └─ OpenStreetMap note  →  Google Drive
                      └─ world Minecraft "Osint"
```

## Tầng cuối — Minecraft *(đang xử lý)*

Trong world có sách hướng dẫn: *"khoảng 20 chiếc rương, chỉ có 1 chiếc chứa thứ bạn cần"*. Một **trapped chest** (bên dưới có 6 khối TNT — bẫy thật) chứa tờ giấy:

```
>2828?4{>282?4C_3?4?6_7?0?4}
```

Đây là bước cuối cần giải mã (đang phân tích trên bản world chuẩn).

## Flag

*Chưa xác nhận — sẽ cập nhật sau khi giải xong tầng Minecraft.*
