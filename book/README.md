# Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp

Đây là mã nguồn LaTeX của sách chuyên khảo do sáu tác giả thực hiện:
Tô Văn Khánh, Kiều Văn Tuyên, Trương Xuân Hiếu, Vũ Thanh Hương,
Đào Xuân Nghĩa và Nguyễn Kim Trung Đức. Sách gồm 11 chương chính và một chương
kết, trình bày nền tảng phép mã hóa SAT, các cấu trúc dùng chung và những
nghiên cứu tình huống trong tối ưu tổ hợp.

Mã nguồn LaTeX gồm ba phần:

1. Nền tảng và tiêu chí thiết kế.
2. Tái sử dụng cấu trúc trong SAT encoding.
3. Các họ bài toán tối ưu tổ hợp.

## Biên dịch

Yêu cầu TeX Live 2025 hoặc tương đương, LuaLaTeX, `latexmk` và `biber`.

```sh
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
```

PDF đầu ra là `main.pdf`. Xóa các tệp trung gian bằng:

```sh
latexmk -c
```

## Cấu trúc

- `main.tex`: bìa, phần đầu, thứ tự các phần/chương, thuật ngữ và thư mục.
- `satbook.sty`: kiểu trình bày, font, màu, định lý, hộp nội dung và thư viện
  phong cách TikZ.
- `vietnamese.lbx`: chuỗi tiếng Việt cho `biblatex`.
- `references.bib`: tài liệu tham khảo thống nhất.
- `chapters/`: mã nguồn 11 chương chính và chương kết.

Sau khi biên dịch, cần kiểm tra danh sách hình, bảng, thuật toán, chỉ mục và
các liên kết tham chiếu trong PDF.

Font được dùng: Libertinus Serif, Libertinus Math, TeX Gyre Heros và
Inconsolata.
