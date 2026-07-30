# Lịch sử thay đổi

Mọi thay đổi đáng chú ý của cuốn sách và mã nguồn xuất bản được ghi tại đây.

## [1.0.0] - 2026-07-30

### Added

- Công bố bản mã nguồn hiệu chỉnh sau phản biện.
- Chuẩn hóa cấu trúc nguồn gồm 11 chương chính và chương kết luận.
- Bổ sung thông tin quyền sử dụng và trích dẫn máy đọc được.
- Bổ sung quy trình build sạch bằng LuaLaTeX, Biber, MakeIndex và `latexmk`.
- Bổ sung kiểm tra tự động số trang, metadata, log và font nhúng của PDF.
- Bổ sung website tĩnh responsive cho GitHub Pages.
- Bổ sung bìa web, Open Graph metadata, sitemap, manifest và trang 404.
- Bổ sung quy trình đóng gói PDF vào website và kiểm tra liên kết nội bộ.
- Sinh bản đọc HTML và gói nguồn LaTeX trực tiếp từ bản thảo hiện tại.
- Dùng `book/` làm nguồn duy nhất; không sử dụng PDF dựng sẵn.
- Kiểm tra dấu vân tay nguồn giữa LaTeX, HTML và các tệp tải xuống.
- Bổ sung GitHub Actions để build, kiểm tra và triển khai lên GitHub Pages.
- Khóa phiên bản action và ảnh TeX Live bằng commit/digest, với quyền triển
  khai tối thiểu và cập nhật Dependabot hàng tháng.
