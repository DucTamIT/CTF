# shopeeee

**Category:** Web

## Đề bài

Sàn thương mại điện tử clone Shopee tại `103.116.52.180`.

## Bước 1: robots.txt

```
User-agent: *
Disallow: /api/

# don't see id 1021x
```

Comment `don't see id 1021x` gợi ý một dải ID quanh `1021x`. `/api/products` chỉ có id 1–40 (ngõ cụt), nhưng order tự tạo lại có id kiểu `102xx` → `1021x` là dải **order ID**.

## Bước 2: IDOR trên `/api/orders/{id}`

Đăng ký một tài khoản thường (`POST /api/auth/register` với `username`, `email`, `password`, `confirm_password`) là có session. Đọc `GET /api/orders/{id}` trả về `200` **bất kể order đó của ai** — không hề kiểm tra quyền sở hữu.

Quét `10210–10239` thấy order **10218** khác thường:

```json
{
  "buyer": {"username": "shoppeee_ops"},
  "payment_method": "INTERNAL",
  "items": [{"name": "Shoppeee Internal Staff Welcome Kit", "unit_price": 0}],
  "total": 0,
  "invoice": {"available": true, "token": "5964ae8e...9e91"}
}
```

Đây là order nội bộ của nhân viên `shoppeee_ops`, và response nhúng luôn **invoice token**.

## Bước 3: IDOR trên `/api/invoices/{token}`

`GET /api/invoices/<token>` cũng không kiểm tra quyền. Invoice loại `INTERNAL` mang thêm vài trường, trong đó `verification_code` chính là flag:

```json
{
  "invoice_type": "INTERNAL",
  "department": "Operations",
  "internal_note": "Quarterly security verification token",
  "verification_code": "miniCTF{sh0ppeee_1d0r_l3ak5_1nv01ce_t0k3n}"
}
```

## Nguyên nhân

**Broken Object Level Authorization (IDOR)** trên cả hai endpoint: chỉ kiểm tra bản ghi tồn tại chứ không kiểm tra nó thuộc về người gọi. Cách sửa: lọc theo `user_id` (hoặc vai trò staff) và trả `404` nếu không khớp.

Script: [`solve.py`](./solve.py)

## Flag

```
miniCTF{sh0ppeee_1d0r_l3ak5_1nv01ce_t0k3n}
```
