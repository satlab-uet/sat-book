#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError:
    print("Cần cài Pillow để tạo tài nguyên website.", file=sys.stderr)
    raise SystemExit(1)


INK = "#172A3A"
BLUE = "#1769AA"
TEAL = "#197278"
GOLD = "#B7791F"
PALE_BLUE = "#F1F6FA"
WHITE = "#FFFFFF"


def find_font(bold: bool) -> Path:
    filename = "texgyreheros-bold.otf" if bold else "texgyreheros-regular.otf"
    kpsewhich = shutil.which("kpsewhich")
    if kpsewhich:
        result = subprocess.run(
            [kpsewhich, filename],
            check=False,
            capture_output=True,
            text=True,
        )
        candidate = Path(result.stdout.strip())
        if result.returncode == 0 and candidate.is_file():
            return candidate

    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        if bold
        else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        if bold
        else Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("Không tìm thấy font sans-serif hỗ trợ tiếng Việt.")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def render_cover(pdf_path: Path, output_dir: Path) -> Image.Image:
    pdftocairo = shutil.which("pdftocairo")
    if not pdftocairo:
        raise FileNotFoundError("Cần cài Poppler để sử dụng pdftocairo.")

    with tempfile.TemporaryDirectory(prefix="sat-book-cover-") as temp_dir:
        output_prefix = Path(temp_dir) / "cover"
        subprocess.run(
            [
                pdftocairo,
                "-f",
                "1",
                "-l",
                "1",
                "-singlefile",
                "-png",
                "-r",
                "180",
                str(pdf_path),
                str(output_prefix),
            ],
            check=True,
        )
        rendered = Image.open(output_prefix.with_suffix(".png")).convert("RGB")
        cover = rendered.resize((720, 1018), Image.Resampling.LANCZOS)

    output_dir.mkdir(parents=True, exist_ok=True)
    cover.save(
        output_dir / "book-cover.webp",
        format="WEBP",
        quality=88,
        method=6,
    )
    return cover


def create_social_card(
    cover: Image.Image,
    output_path: Path,
    regular_path: Path,
    bold_path: Path,
) -> None:
    card = Image.new("RGB", (1200, 630), WHITE)
    draw = ImageDraw.Draw(card)

    draw.rectangle((0, 0, 1200, 10), fill=BLUE)
    draw.rectangle((575, 0, 875, 10), fill=TEAL)
    draw.rectangle((875, 0, 1200, 10), fill=GOLD)
    draw.ellipse((930, -160, 1320, 230), outline="#D6E5EF", width=2)
    draw.ellipse((1010, 380, 1280, 650), outline="#D9ECEA", width=2)

    cover_height = 510
    cover_width = round(cover.width * cover_height / cover.height)
    small_cover = cover.resize(
        (cover_width, cover_height),
        Image.Resampling.LANCZOS,
    )
    draw.rounded_rectangle(
        (64, 68, 64 + cover_width + 18, 68 + cover_height + 18),
        radius=8,
        fill="#D7E0E6",
    )
    card.paste(small_cover, (55, 55))

    draw.text(
        (450, 72),
        "CHUYÊN KHẢO · PHIÊN BẢN 1.0.0",
        font=font(bold_path, 22),
        fill=BLUE,
    )
    draw.text(
        (450, 128),
        "BIỂU DIỄN",
        font=font(bold_path, 68),
        fill=INK,
        stroke_width=0,
    )
    draw.text(
        (450, 205),
        "SAT TỐI ƯU",
        font=font(bold_path, 68),
        fill=INK,
        stroke_width=0,
    )
    draw.multiline_text(
        (452, 310),
        "cho các bài toán\ntối ưu hóa tổ hợp",
        font=font(regular_path, 34),
        fill="#2F4353",
        spacing=8,
    )
    draw.line((452, 442, 1110, 442), fill="#CBD5DC", width=2)
    draw.text(
        (452, 474),
        "Nền tảng · Thiết kế · Tái sử dụng cấu trúc",
        font=font(bold_path, 24),
        fill=TEAL,
    )
    draw.text(
        (452, 536),
        "SATLab · UET",
        font=font(bold_path, 26),
        fill=INK,
    )
    draw.rounded_rectangle((1050, 526, 1127, 576), radius=7, fill=INK)
    draw.text(
        (1064, 538),
        "SAT",
        font=font(bold_path, 20),
        fill=WHITE,
    )

    card.save(output_path, format="PNG", optimize=True)


def create_icon(output_path: Path, size: int, bold_path: Path) -> None:
    icon = Image.new("RGB", (size, size), PALE_BLUE)
    draw = ImageDraw.Draw(icon)
    radius = max(4, round(size * 0.14))
    inset = max(1, round(size * 0.045))
    draw.rounded_rectangle(
        (inset, inset, size - inset - 1, size - inset - 1),
        radius=radius,
        fill=INK,
    )
    stripe_height = max(2, round(size * 0.08))
    draw.rectangle(
        (inset, size - inset - stripe_height, size - inset - 1, size - inset - 1),
        fill=BLUE,
    )
    label_font = font(bold_path, max(10, round(size * 0.29)))
    bounds = draw.textbbox((0, 0), "SAT", font=label_font)
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    draw.text(
        ((size - text_width) / 2, (size - text_height) / 2 - bounds[1] - size * 0.01),
        "SAT",
        font=label_font,
        fill=WHITE,
    )
    icon.save(output_path, format="PNG", optimize=True)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    pdf_path = repo_root / "build" / "main.pdf"
    output_dir = repo_root / "site" / "assets" / "images"

    if not pdf_path.is_file():
        print(f"Không tìm thấy PDF: {pdf_path}", file=sys.stderr)
        print("Hãy chạy `make book` trước.", file=sys.stderr)
        return 1

    try:
        regular_path = find_font(bold=False)
        bold_path = find_font(bold=True)
        cover = render_cover(pdf_path, output_dir)
        create_social_card(
            cover,
            output_dir / "og-card.png",
            regular_path,
            bold_path,
        )
        create_icon(output_dir / "favicon-32.png", 32, bold_path)
        create_icon(output_dir / "apple-touch-icon.png", 180, bold_path)
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1

    print(f"Đã tạo tài nguyên website tại: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
