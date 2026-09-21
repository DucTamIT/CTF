# Bird Runner

**Category:** Web

## Đề bài

Web game kiểu Flappy Bird tại `103.116.52.180`. Người chơi điều khiển chim, khi thua thì bấm **Submit** để nộp điểm.

## Phân tích

Xem [`files/game.js`](./files/game.js). Khi nộp điểm, client tính một checksum rồi gửi lên server:

```js
const checksum = zx(session.token, finalScore, session.nonce);
fetch("/api/game/submit", { ...
  body: JSON.stringify({ session_id, score: finalScore, checksum }) });
```

Toàn bộ hàm `zx()` (một hash 64-bit tự chế) **nằm ngay trong JS client**, cùng với 5 hằng số `K1..K5`. Server chỉ kiểm tra `checksum == zx(token, score, nonce)` chứ không xác minh điểm có thực sự chơi ra hay không. Vì thế ta tự tính checksum cho **bất kỳ điểm nào** rồi nộp thẳng qua API, không cần chơi.

## Khai thác

1. `POST /api/game/start` → nhận `session_id`, `token`, `nonce`.
2. Reimplement `zx()` bằng Python (chú ý dùng phép nhân 32-bit `Math.imul`).
3. Tính checksum cho điểm `1_000_000_000` (server có `"target": 1000000000`).
4. `POST /api/game/submit` với `session_id`, `score`, `checksum`.

Script: [`solve.py`](./solve.py)

```
$ python solve.py
flag: miniCTF{Kh0N9_pHA1_AN_Cap_Y_7uoN6_7U_DIn0ruNN3r_D4U_nhe_<E}
```

Server trả về: `Score submitted: 1000000000 - Rank: #1 - the bird has transcended.`

## Flag

```
miniCTF{Kh0N9_pHA1_AN_Cap_Y_7uoN6_7U_DIn0ruNN3r_D4U_nhe_<E}
```
