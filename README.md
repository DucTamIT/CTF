# Write-up: Tìm Flag Website ISPClub

Do đây là một bài warmup đơn giản nên ta sẽ tìm ở những nơi mắt thường có thể thấy. Sau khoảng 5 phút loanh quanh, ta sẽ thấy các flag sau.

## Flag 1 

**Link:** `https://ispclub.vn/contribute`

```
ISPCLUB{n4h_4r3_U_g4y_l1k3_M1nhnl?}
```

## Flag 2, 3, 4 

**Link:** `https://ispclub.vn/blog`

| Bài viết | Flag |
|---|---|
| SVATTT CTF 2024 Writeup | `ISPCLUB{c4n_y0u_s33?}` |
| Reverse Engineering Fundamentals Guide | `ISPCLUB{1nt3rn3t_5ev1c3_pr0v1d3r}` |
| Advanced SQL Injection Analysis | `ISPCLUB{1_d0n't_kn0w_wh4t_15_th4t}` |

## Flag 5

**Link:** `https://ispclub.vn/events`

```
ISPCLUB{h3ll0_h3ckeR}
```

## Flag 6

Sau khi chắc chắn tất cả các trang không còn flag dễ thấy nào khác, mở DevTools -> Network, load hết các endpoint và search `"ISPCLUB{"`. Flag tiếp theo nằm trong source code của trang `https://ispclub.vn/members`

```html
<!-- ISPCLUB{w3llc0m3_to_15P_CLU13} -->
```

```
ISPCLUB{w3llc0m3_to_15P_CLU13}
```

## Flag 7 

Do không còn search được nữa, chắc chắn flag còn lại đã bị encode, khả năng cao là Base64. Tuy nhiên, do cơ chế chunking của Base64, không thể search trực tiếp chuỗi `"SVNQQ0xVQns"` (`"ISPCLUB{"`).

Sau khi kiểm tra source của tất cả các endpoint, phát hiện chuỗi sau tại: `https://ispclub.vn/achievements`

**Chuỗi Base64:**
```
xJHDonkgbMOgIHRow7RuZyB0aW4gYuG6o28gbeG6rXQgbGnDqm4gcXVhbiB04bubaSBjaGluaHBodS52biwgbeG7jWkgaMOgbmggdmkgxJHhu41jIHdlYiwgdGjhu7FjIGhp4buHbiB0aHUgdGjhuq1wIGThu68gbGnhu4d1IMSR4buBdSBi4buLIHThu6sgY2jhu5FpIHRyb25nIMSRw7MgY8OzIElTUENMVUJ7aDNoM180cnIzX3kwdV9yMzRkeT99
```

**Sau khi giải mã:**
```
đây là thông tin bảo mật liên quan tới chinhphu.vn, mọi hành vi đọc web, thực hiện thu thập dữ liệu đều bị từ chối trong đó có ISPCLUB{h3h3_4rr3_y0u_r34dy?}
```

**Flag 7:**
```
ISPCLUB{h3h3_4rr3_y0u_r34dy?}
```
