# Last Sync

Category: Forensics / Network
Difficulty: Easy–Medium
Flag format: miniCTF{...}

Một máy trạm trong mạng nội bộ bị nghi đã làm rò rỉ một thông điệp. Đội giám sát chỉ kịp lưu lại traffic trong một khoảng thời gian ngắn.

> Phân tích capture.pcap và tìm flag.

## Files

- capture.pcap — network capture cần phân tích.

## Hints

1. Không phải request nào cũng mang dữ liệu cần tìm.
2. Các mảnh của cùng một lần đồng bộ có số thứ tự riêng; timestamp của packet không phải thứ tự ghép cuối cùng.
3. Sau khi ghép dữ liệu, hãy nhận diện lớp mã hoá/nén tiếp theo.

## Rules

- Không cần kết nối Internet hay truy cập hệ thống bên ngoài.
- Chỉ submit flag theo đúng format miniCTF{...}.
