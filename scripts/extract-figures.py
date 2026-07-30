#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

def crop_diagram_content(im: Image.Image, padding: int = 24) -> Image.Image:
    """Crop the exact diagram area from the page."""
    width, height = im.size
    top_crop = int(height * 0.15)
    bottom_crop = int(height * 0.85)
    
    cropped_page = im.crop((0, top_crop, width, bottom_crop))
    
    bg = Image.new(cropped_page.mode, cropped_page.size, (255, 255, 255))
    diff = ImageChops.difference(cropped_page, bg)
    bbox = diff.getbbox()
    if bbox:
        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(cropped_page.width, bbox[2] + padding)
        bottom = min(cropped_page.height, bbox[3] + padding)
        return cropped_page.crop((left, top, right, bottom))
    return cropped_page

def main():
    repo_root = Path(__file__).resolve().parent.parent
    pdf_path = repo_root / "build" / "main.pdf"
    output_dir = repo_root / "site" / "assets" / "images" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)

    pdftocairo = shutil.which("pdftocairo")
    if not pdftocairo:
        print("pdftocairo not found, skipping PDF figure extraction.", file=sys.stderr)
        return

    # Verified page numbers in authoritative PDF (outputs/sat_book_2026/latex_reviewed_book/main.pdf)
    key_figures = [
        {"id": "fig_ch01", "page": 18, "title": "Sơ đồ vòng lặp CDCL trong bộ giải SAT"},
        {"id": "fig_ch03", "page": 30, "title": "Lưới trạng thái bộ đếm tuần tự (Sequential Counter)"},
        {"id": "fig_ch04", "page": 38, "title": "Hồ sơ hiệu năng dạng bậc thang (Performance Profile)"},
        {"id": "fig_ch05", "page": 45, "title": "Bộ đếm dùng chung cho các cửa sổ chồng lấn (Shared Counter)"},
        {"id": "fig_ch06", "page": 51, "title": "Thanh ghi đếm thích nghi và miền trạng thái tam giác (NSC)"},
        {"id": "fig_ch07", "page": 57, "title": "Quỹ đạo đại diện phá đối xứng (Symmetry Breaking)"},
        {"id": "fig_ch08", "page": 67, "title": "Cửa sổ ALSC tái sử dụng trong bài toán lập lịch"},
        {"id": "fig_ch09", "page": 74, "title": "Bố trí nguyên và biến chứng quan hệ tách trong đóng gói 2D"},
        {"id": "fig_ch10", "page": 82, "title": "Cặp nhãn bị cấm và bài toán Antibandwidth trên đồ thị"},
        {"id": "fig_ch11", "page": 88, "title": "Gán nhãn radio khả thi và nén khoảng cấm"},
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
                    "-r", "300",
                    str(pdf_path),
                    str(out_prefix)
                ],
                check=True
            )
            
            rendered_png = out_prefix.with_suffix(".png")
            if rendered_png.exists():
                im = Image.open(rendered_png).convert("RGB")
                trimmed = crop_diagram_content(im)
                
                webp_path = output_dir / f"{fig_id}.webp"
                trimmed.save(webp_path, format="WEBP", quality=95, method=6)
                print(f"[✓] Extracted exact diagram: {webp_path.name} (page {page_num}, {trimmed.width}x{trimmed.height}px)")

if __name__ == "__main__":
    main()
