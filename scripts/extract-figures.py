#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

def trim_whitespace(im: Image.Image, padding: int = 24) -> Image.Image:
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(im.width, bbox[2] + padding)
        bottom = min(im.height, bbox[3] + padding)
        return im.crop((left, top, right, bottom))
    return im

def main():
    repo_root = Path(__file__).resolve().parent.parent
    pdf_path = repo_root / "build" / "main.pdf"
    output_dir = repo_root / "site" / "assets" / "images" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)

    pdftocairo = shutil.which("pdftocairo")
    if not pdftocairo:
        print("pdftocairo not found, skipping PDF figure extraction.", file=sys.stderr)
        return

    # Key figure pages map (Chapter -> Page Number in PDF)
    key_figures = [
        {"id": "fig_ch01", "page": 5, "title": "Sơ đồ vòng lặp CDCL trong bộ giải SAT", "chap": "Phần I · Chương 1"},
        {"id": "fig_ch03", "page": 17, "title": "Lưới trạng thái bộ đếm tuần tự (Sequential Counter)", "chap": "Phần I · Chương 3"},
        {"id": "fig_ch04", "page": 25, "title": "Hồ sơ hiệu năng dạng bậc thang (Performance Profile)", "chap": "Phần I · Chương 4"},
        {"id": "fig_ch05", "page": 32, "title": "Bộ đếm dùng chung cho các cửa sổ chồng lấn (Shared Counter)", "chap": "Phần II · Chương 5"},
        {"id": "fig_ch06", "page": 38, "title": "Thanh ghi đếm thích nghi và miền trạng thái tam giác (NSC)", "chap": "Phần II · Chương 6"},
        {"id": "fig_ch07", "page": 44, "title": "Quỹ đạo đại diện phá đối xứng (Symmetry Breaking)", "chap": "Phần II · Chương 7"},
        {"id": "fig_ch08", "page": 54, "title": "Cửa sổ ALSC tái sử dụng trong bài toán lập lịch", "chap": "Phần III · Chương 8"},
        {"id": "fig_ch09", "page": 61, "title": "Bố trí nguyên và biến chứng quan hệ tách trong đóng gói 2D", "chap": "Phần III · Chương 9"},
        {"id": "fig_ch10", "page": 69, "title": "Cặp nhãn bị cấm và bài toán Antibandwidth trên đồ thị", "chap": "Phần III · Chương 10"},
        {"id": "fig_ch11", "page": 76, "title": "Gán nhãn radio khả thi và nén khoảng cấm", "chap": "Phần III · Chương 11"},
    ]

    with tempfile.TemporaryDirectory(prefix="sat-fig-extract-") as temp_dir:
        for item in key_figures:
            page_num = item["page"]
            fig_id = item["id"]
            out_prefix = Path(temp_dir) / f"{fig_id}"
            
            subprocess.run(
                [
                    pdftocairo,
                    "-f", str(page_num),
                    "-l", str(page_num),
                    "-singlefile",
                    "-png",
                    "-r", "200",
                    str(pdf_path),
                    str(out_prefix)
                ],
                check=True
            )
            
            rendered_png = out_prefix.with_suffix(".png")
            if rendered_png.exists():
                im = Image.open(rendered_png).convert("RGB")
                trimmed = trim_whitespace(im, padding=30)
                
                # Save as WebP
                webp_path = output_dir / f"{fig_id}.webp"
                trimmed.save(webp_path, format="WEBP", quality=90, method=6)
                print(f"Extracted figure: {webp_path.name} (page {page_num})")

if __name__ == "__main__":
    main()
