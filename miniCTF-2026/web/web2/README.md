# web2

**Category:** Web

## Đề bài

"JWT Security Lab" tại `103.116.52.180:45151`. Đăng ký / đăng nhập để quan sát cách server cấp và kiểm tra token.

## Phân tích

Đăng nhập trả về cookie `token` là một **JWT HS256**:

```
header:  {"alg":"HS256","typ":"JWT"}
payload: {"id":1,"username":"...","role":"user","iat":...,"exp":...}
```

Route `/flag` yêu cầu `role: admin`, với token thường thì trả `Access denied: Bạn không phải admin`.

Không biết secret nên không ký lại được token HS256. Nhưng thử đổi **`alg` trong JWT header** thành `none` — kiểu tấn công kinh điển khi server chấp nhận thuật toán `none` (token không cần chữ ký).

## Khai thác

Rèn một token với:
- header `{"alg":"none","typ":"JWT"}`
- payload đổi `"role":"admin"`
- **chữ ký rỗng** (phần thứ 3 để trống, vẫn giữ dấu chấm)

```
base64url({"alg":"none","typ":"JWT"}) . base64url({...,"role":"admin"}) .
```

Gửi qua cookie `token`:

```
GET /flag   Cookie: token=<forged>
→ miniCTF{jwt_none_alg_hehehehe}
```

Lưu ý: server chỉ chấp nhận token qua **cookie `token`**, không nhận `Authorization: Bearer`.

Script: [`solve.py`](./solve.py)

## Flag

```
miniCTF{jwt_none_alg_hehehehe}
```
