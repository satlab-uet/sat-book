# Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp

[![Deploy book to GitHub Pages](https://github.com/satlab-uet/sat-book/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/satlab-uet/sat-book/actions/workflows/deploy-pages.yml)

Mã nguồn LaTeX của chuyên khảo:

**Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp**

*Khảo cứu nền tảng và các họ mã hóa; nguyên lý thiết kế và tái sử dụng
cấu trúc; nghiên cứu tình huống trong tối ưu tổ hợp.*

## Tác giả

- Tô Văn Khánh
- Kiều Văn Tuyên
- Trương Xuân Hiếu
- Vũ Thanh Hương
- Đào Xuân Nghĩa
- Nguyễn Kim Trung Đức

## Phiên bản

Phiên bản `1.0.0`, bản hiệu chỉnh sau phản biện ngày 30/07/2026.

Sách gồm ba phần, 11 chương chính và một chương kết luận. Bản PDF chuẩn có
106 trang A4. Các hình kỹ thuật được dựng nguyên bản bằng TikZ trong mã nguồn.

## Cấu trúc

```text
book/
├── main.tex
├── satbook.sty
├── vietnamese.lbx
├── references.bib
└── chapters/
    ├── ch01-foundations.tex
    ├── ...
    ├── ch11-labeling.tex
    └── conclusion.tex
```

- `book/main.tex`: bìa, phần đầu sách và thứ tự các phần/chương.
- `book/satbook.sty`: kiểu trình bày, font, màu, định lý, hộp nội dung và TikZ.
- `book/vietnamese.lbx`: chuỗi tiếng Việt cho `biblatex`.
- `book/references.bib`: thư mục tài liệu tham khảo.
- `book/chapters/`: mã nguồn các chương.

## Yêu cầu biên dịch

- TeX Live 2025 hoặc tương đương.
- LuaLaTeX.
- `latexmk`.
- Biber.
- MakeIndex.

Các font được dùng là Libertinus Serif, Libertinus Math, TeX Gyre Heros và
Inconsolata.

Để chạy bước kiểm tra PDF, cần thêm Poppler (`pdfinfo`, `pdffonts`,
`pdftotext`).

## Biên dịch

Từ thư mục gốc của repository:

```sh
make book
```

PDF đầu ra:

```text
build/main.pdf
```

Biên dịch và kiểm tra:

```sh
make check
```

Tạo website tĩnh kèm PDF:

```sh
make site
```

Tạo lại bìa web, ảnh chia sẻ mạng xã hội và biểu tượng từ trang đầu PDF:

```sh
make site-assets
```

Tạo và kiểm tra cả website:

```sh
make check-site
```

Website đầu ra nằm trong `_site/`. Mọi đường dẫn nội bộ sử dụng cấu trúc tương
thích với GitHub Pages tại `/sat-book/`.

Website chính thức:

<https://satlab-uet.github.io/sat-book/>

Lệnh `make site-assets` cần thêm Python 3, Pillow và Poppler. Các tài nguyên đã
sinh được lưu trong `site/assets/images/`, vì vậy bước đóng gói `make site`
không phụ thuộc vào Pillow.

## Triển khai GitHub Pages

Workflow `.github/workflows/deploy-pages.yml` biên dịch lại sách bằng TeX Live
2025, kiểm tra PDF, đóng gói website và chỉ triển khai khi toàn bộ kiểm tra
thành công. Pull request vào `main` chỉ chạy build và kiểm tra; không được phép
triển khai.

Workflow sử dụng quyền tối thiểu theo từng job. Các action và Docker image đều
được khóa bằng commit hoặc digest; Dependabot kiểm tra cập nhật action hàng
tháng.

Xóa toàn bộ kết quả build:

```sh
make clean
```

Quá trình build ghi tất cả tệp trung gian vào `build/`; mã nguồn trong
`book/` không bị trộn với tệp sinh tự động.

## Định dạng HTML

Website hiện cung cấp PDF là bản tham chiếu chính thức. Bản HTML toàn văn đang
được phát triển trực tiếp từ nguồn LaTeX. Các thử nghiệm tự động với TeX4ht và
LaTeXML cho thấy cần bổ sung ánh xạ riêng cho `satbook.sty`, KOMA-Script,
`tcolorbox` và TikZ trước khi kết quả đủ tin cậy để công bố.

## Trích dẫn

Thông tin trích dẫn máy đọc được nằm trong [`CITATION.cff`](CITATION.cff).
Khi trích dẫn, vui lòng dùng mục `preferred-citation`.

## Báo lỗi

Vui lòng tạo issue tại:

<https://github.com/satlab-uet/sat-book/issues>

Khi báo lỗi nội dung, nên ghi rõ số trang, chương/mục, đoạn liên quan và đề
xuất sửa nếu có.

## Quyền sử dụng

Copyright © 2026 các tác giả. All rights reserved.

Việc repository được công khai không đồng nghĩa với việc cấp giấy phép sao
chép, phân phối, sửa đổi, dịch hoặc tạo tác phẩm phái sinh. Xem
[`LICENSE`](LICENSE) để biết chi tiết.
