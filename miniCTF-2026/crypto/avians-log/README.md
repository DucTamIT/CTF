# Avian's Log

**Category:** Crypto

## Đề bài

> Chú chim đưa thư của vương quốc vừa hoàn thành một chuyến bay do thám quan trọng. Thay vì ghi chép tọa độ thông thường, nó lưu lại chuỗi cảnh vật, sinh vật và tinh tú mà nó gặp trên đường. Các thợ săn chim của ISP tin rằng chuỗi cảnh vật này không phải là một đường bay ngẫu nhiên, mà là một bản tin tình báo đã được chuyển đổi qua một quy luật **64 cơ số**.

Đề cho 2 file (xem thư mục [`files/`](./files/)):

- `bird_memory.txt`: một dãy **65 emoji**.
  ```
  🦊🐻🐼🐨🐯🦁🐮🐷🐸🐵🐔🐧🐦🐤🦆🦅🌲🌳🌴🌵🌾🌿🍀🍁🍂🍃🍄🌷🌹🌺🌻🌼🍇🍈🍉🍊🍋🍌🍍🥭🍎🍏🍐🍑🍒🍓🥝🍅🌍🌎🌏🌕🌖🌗🌘🌑🌒🌓🌔🌙🪐🌟🌠🌌🥚
  ```
- `journey.txt`: bản tin cần giải, gồm 44 emoji.
  ```
  🌷🍀🍌🥝🍄🌾🐤🌾🌳🥭🍓🥝🐦🐷🌳🌼🐤🦁🌟🌏🐤🐮🌓🍋🐦🐮🌗🌼🍃🍍🌍🌎🍃🌘🍈🌖🍁🌑🦊🌖🌺🐮🍈🌟
  ```

## Phân tích

"Quy luật 64 cơ số" chính là **Base64**. Bảng chữ cái Base64 có 64 ký tự cộng thêm ký tự padding `=`, tổng cộng 65, khớp đúng với số emoji trong `bird_memory.txt`:

- 64 emoji đầu (động vật → cây cỏ → hoa quả → tinh tú) ứng với 64 ký tự `A-Z a-z 0-9 + /`, theo đúng thứ tự.
- Emoji cuối cùng 🥚 là padding `=`.

Do đó `bird_memory.txt` chính là **bảng chữ cái Base64 đã bị thay bằng emoji**, còn `journey.txt` là chuỗi Base64 viết bằng bảng chữ cái đó.

| Emoji | 🦊 | 🐻 | ... | 🦅 | 🌲 | ... | 🌌 | 🥚 |
|---|---|---|---|---|---|---|---|---|
| Index | 0 | 1 | ... | 15 | 16 | ... | 63 | pad |
| Base64 | `A` | `B` | ... | `P` | `Q` | ... | `/` | `=` |

## Giải

Thay mỗi emoji trong `journey.txt` bằng ký tự Base64 tương ứng, ta được:

```
bWluaUNURntuMHRfNF9yNG5kMG1fZmwxZ2h0X3A0dGh9
```

Decode Base64 là ra flag. Script đầy đủ: [`solve.py`](./solve.py)

```
$ python solve.py
base64: bWluaUNURntuMHRfNF9yNG5kMG1fZmwxZ2h0X3A0dGh9
flag:   miniCTF{n0t_4_r4nd0m_fl1ght_p4th}
```

## Flag

```
miniCTF{n0t_4_r4nd0m_fl1ght_p4th}
```
