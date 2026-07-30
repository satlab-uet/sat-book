# Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp

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

Xóa toàn bộ kết quả build:

```sh
make clean
```

Quá trình build ghi tất cả tệp trung gian vào `build/`; mã nguồn trong
`book/` không bị trộn với tệp sinh tự động.

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
