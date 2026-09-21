# Last Sync

**Category:** Forensics / Network

## Đề bài

> Một máy trạm trong mạng nội bộ bị nghi đã làm rò rỉ một thông điệp. Đội giám sát chỉ kịp lưu lại traffic trong một khoảng thời gian ngắn. Phân tích `capture.pcap` và tìm flag.

Hints:
1. Không phải request nào cũng mang dữ liệu cần tìm.
2. Các mảnh của cùng một lần đồng bộ có số thứ tự riêng; timestamp của packet không phải thứ tự ghép cuối cùng.
3. Sau khi ghép dữ liệu, hãy nhận diện lớp mã hoá/nén tiếp theo.

File đề: [`files/`](./files/)

## Phân tích

Pcap chỉ có HTTP giữa `10.13.37.20` và `telemetry.local`. Mở bằng Wireshark với filter `http.request`:

| Request | Ghi chú |
|---|---|
| `/health`, `/assets/app.js`, `/api/heartbeat` | Nhiễu |
| `/api/status?message=miniCTF{not_the_flag}` | Decoy |
| `/telemetry/sync?session=debug&part=1..2` | Base64 → `heartbeat:1`, `heartbeat:2` |
| `/telemetry/sync?session=old-91&part=1..2` | Base64 → `retry:1`, `retry:2` |
| `/telemetry/sync?session=4f2a&part=X&total=6` | **6 mảnh dữ liệu thật** |

Chỉ session `4f2a` có tham số `total=6`, và các mảnh của nó được gửi **không theo thứ tự**: 4, 1, 6, 2, 5, 3.

## Giải

Sắp các mảnh theo `part` (không theo thời gian), rồi URL-decode:

| part | data |
|---|---|
| 1 | `H4sIAAAAAAAC` |
| 2 | `/8vNzMt0DnGr` |
| 3 | `Lkg2KYjPNjaI` |
| 4 | `TynNs4w3zyiN` |
| 5 | `Ny+NTzcwrAUA` |
| 6 | `b1k/viEAAAA=` |

Ghép lại được một chuỗi Base64 bắt đầu bằng `H4sI`, đây là dấu hiệu của **gzip** (`1f 8b`). Base64 decode rồi gunzip là ra flag.

Script: [`solve.py`](./solve.py)

```
base64: H4sIAAAAAAAC/8vNzMt0DnGrLkg2KYjPNjaITynNs4w3zyiNNy+NTzcwrAUAb1k/viEAAAA=
magic: 1f8b
flag: miniCTF{pc4p_k30_dun9_7hu_7u_g01}
```

## Flag

```
miniCTF{pc4p_k30_dun9_7hu_7u_g01}
```
