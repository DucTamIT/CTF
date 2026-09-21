# Socola Bạc Hà

**Category:** OSINT

## Đề bài

> Người dùng facebook với username `socolabachaptit` đang giấu thứ gì đó trong facebook của anh ấy. Hãy thử tìm hiểu xem

## Nửa sau của flag: Bio Facebook

Vào Facebook `socolabachaptit`, phần **bio** có sẵn nửa sau của flag:

```
_soc0la_bac_ha}
```

## Nửa đầu của flag: Google Maps review

Lục trong **Albums** của anh ấy, trong một folder ảnh có ảnh `cmt.png` với nội dung:

> Chúc mừng bạn đã tìm ra tôi
> Thực ra tôi thích socola dâu 🙁
> #xinloivisuphanboi
> Lâu đài Chocolate là 1 trong những địa điểm yêu thích của tôi, tôi đã 1 lần đến đó tuy nhiên nơi đó đã trở thành nơi trưng bày và chỉ còn là những kỷ niệm.
> `11.971491,108.421871`
> Tôi đã có những đánh giá khá thú vị về nó.

Tra toạ độ `11.971491,108.421871` trên Google Maps ra địa điểm **La Chocotea** (Đà Lạt). Trong phần **Reviews** có một ảnh do tài khoản *Bạc Hà Socola* đăng: nền trắng với một hình xoắn ốc, tức là chữ đã bị làm méo bằng hiệu ứng **Twirl**.

Mở ảnh trong Photoshop, vào **Filter → Distort → Twirl** và chỉnh góc (khoảng 542°) để xoắn ngược lại:

![Twirl](./images/twirl.png)

Chữ hiện ra rõ ràng:

![Flag](./images/untwirled.png)

```
miniCTF{0s1nt_thu_vi_nhw
```

## Flag

Ghép 2 nửa lại:

```
miniCTF{0s1nt_thu_vi_nhw_soc0la_bac_ha}
```
