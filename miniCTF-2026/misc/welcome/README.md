# Welcome

**Category:** Misc

## Đề bài

Đề cho file [`files/welcome_MiniCTF.md`](./files/welcome_MiniCTF.md): một đoạn văn kể về chú chim bị nhốt trong lồng, mong được bay ra bầu trời tự do. Cuối file có link:

```
Link: https://ispclub.vn
```

## Phân tích

Trong cả đoạn văn chỉ có một cụm từ được **in đậm và in nghiêng** (`***...***`):

> Hôm nay, nhìn qua nan lồng chật hẹp, mắt tôi dừng lại phía chân trời. ***Chú chim đầu đàn*** đang dẫn dắt bầy chim con sải cánh bay vút lên bầu trời tự do.

"Chú chim đầu đàn" là người dẫn dắt cả đàn, tức là **người đứng đầu CLB**. Kết hợp với link `https://ispclub.vn`, ta cần tìm thông tin về **chủ tịch hiện tại của ISP Club**.

## Khai thác

1. Vào website `https://ispclub.vn`.
2. Mở trang **Thành viên** (`https://ispclub.vn/members`).
3. Tìm tới **Chủ tịch CLB hiện tại**. Flag nằm ở phần thông tin của người này.

## Flag

```
miniCTF{H3l10_m1niCtF_2o26}
```
