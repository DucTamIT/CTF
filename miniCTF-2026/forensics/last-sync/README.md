# Last Sync

**Category:** Forensics / Network

## Đề bài

> Một máy trạm trong mạng nội bộ bị nghi đã làm rò rỉ một thông điệp. Đội giám sát chỉ kịp lưu lại traffic trong một khoảng thời gian ngắn. Phân tích `capture.pcap` và tìm flag.

Hints:
1. Không phải request nào cũng mang dữ liệu cần tìm.
2. Các mảnh của cùng một lần đồng bộ có số thứ tự riêng; timestamp của packet không phải thứ tự ghép cuối cùng.
3. Sau khi ghép dữ liệu, hãy nhận diện lớp mã hoá/nén tiếp theo.

File đề: [`files/`](./files/)

## Giải bằng Wireshark

**1. Lọc HTTP request.** Mở `capture.pcap` bằng Wireshark, filter:

```
http.request
```

Trong cột Info có các request tới `telemetry.local`:

| Request | Ghi chú |
|---|---|
| `/health`, `/assets/app.js`, `/api/heartbeat` | Nhiễu |
| `/api/status?message=miniCTF{not_the_flag}` | Decoy |
| `/telemetry/sync?session=debug&part=1..2` | Base64 → `heartbeat:1`, `heartbeat:2` |
| `/telemetry/sync?session=old-91&part=1..2` | Base64 → `retry:1`, `retry:2` |
| `/telemetry/sync?session=4f2a&part=X&total=6` | **6 mảnh dữ liệu thật** |

**2. Chỉ giữ session thật.** Session `4f2a` là session duy nhất có `total=6` (Hint 1: không phải request nào cũng mang dữ liệu). Lọc riêng các request này:

```
http.request.uri contains "session=4f2a"
```

Các mảnh được gửi theo thứ tự **4, 1, 6, 2, 5, 3**, không đúng thứ tự (Hint 2).

**3. Sắp theo `part`.** Đọc tham số `data` của từng request (nhớ URL-decode `%2F` → `/`, `%2B` → `+`, `%3D` → `=`) rồi xếp theo `part`:

| part | data |
|---|---|
| 1 | `H4sIAAAAAAAC` |
| 2 | `/8vNzMt0DnGr` |
| 3 | `Lkg2KYjPNjaI` |
| 4 | `TynNs4w3zyiN` |
| 5 | `Ny+NTzcwrAUA` |
| 6 | `b1k/viEAAAA=` |

Ghép lại:

```
H4sIAAAAAAAC/8vNzMt0DnGrLkg2KYjPNjaITynNs4w3zyiNNy+NTzcwrAUAb1k/viEAAAA=
```

**4. Giải mã.** Chuỗi Base64 bắt đầu bằng `H4sI` là dấu hiệu của **gzip** (magic `1f 8b`) (Hint 3). Dán vào CyberChef với recipe **From Base64 → Gunzip** là ra flag.

Script tự động (không bắt buộc): [`solve.py`](./solve.py)

## Flag

```
miniCTF{pc4p_k30_dun9_7hu_7u_g01}
```
