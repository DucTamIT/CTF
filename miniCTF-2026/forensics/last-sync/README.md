# Last Sync

**Category:** Forensics / Network

## Đề bài

> Một máy trạm trong mạng nội bộ bị nghi đã làm rò rỉ một thông điệp. Đội giám sát chỉ kịp lưu lại traffic trong một khoảng thời gian ngắn. Phân tích `capture.pcap` và tìm flag.

Hints:
1. Không phải request nào cũng mang dữ liệu cần tìm.
2. Các mảnh của cùng một lần đồng bộ có số thứ tự riêng; timestamp của packet không phải thứ tự ghép cuối cùng.
3. Sau khi ghép dữ liệu, hãy nhận diện lớp mã hoá/nén tiếp theo.

File đề: [`files/`](./files/)

## Giải

Mở `capture.pcap` bằng Wireshark và đọc lần lượt từng HTTP request. Trong số đó có các request `/telemetry/sync?session=4f2a&part=X&total=6&data=...` mang tham số `part` và `data`. Các request còn lại chỉ là nhiễu hoặc decoy (`miniCTF{not_the_flag}`, `heartbeat`, `retry`).

Các mảnh bị gửi lộn xộn, nên xếp lại theo `part` (URL-decode `%2F` → `/`, `%3D` → `=`):

| part | data |
|---|---|
| 1 | `H4sIAAAAAAAC` |
| 2 | `/8vNzMt0DnGr` |
| 3 | `Lkg2KYjPNjaI` |
| 4 | `TynNs4w3zyiN` |
| 5 | `Ny+NTzcwrAUA` |
| 6 | `b1k/viEAAAA=` |

Ghép lại được một chuỗi Base64 bắt đầu bằng `H4sI`, tức là **gzip**. Dán vào CyberChef, chạy **From Base64 → Gunzip** là ra flag.

## Flag

```
miniCTF{pc4p_k30_dun9_7hu_7u_g01}
```
