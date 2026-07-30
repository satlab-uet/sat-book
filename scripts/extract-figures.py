#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

# Verified exact TikZ diagram bounding boxes (top_y, bottom_y) on 300 DPI page renders
EXACT_FIGURE_CROP_MAP = {
    "fig_ch01": {"page": 18, "top_y": 280, "bottom_y": 700, "title": "Sơ đồ vòng lặp CDCL trong bộ giải SAT"},
    "fig_ch03": {"page": 30, "top_y": 440, "bottom_y": 760, "title": "Lưới trạng thái bộ đếm tuần tự (Sequential Counter)"},
    "fig_ch04": {"page": 38, "top_y": 390, "bottom_y": 900, "title": "Hồ sơ hiệu năng dạng bậc thang (Performance Profile)"},
    "fig_ch05": {"page": 45, "top_y": 900, "bottom_y": 1460, "title": "Bộ đếm dùng chung cho các cửa sổ chồng lấn (Shared Counter)"},
    "fig_ch06": {"page": 51, "top_y": 2100, "bottom_y": 2480, "title": "Thanh ghi đếm thích nghi và miền trạng thái tam giác (NSC)"},
    "fig_ch07": {"page": 57, "top_y": 2120, "bottom_y": 2540, "title": "Quỹ đạo đại diện phá đối xứng (Symmetry Breaking)"},
    "fig_ch08": {"page": 67, "top_y": 1860, "bottom_y": 2080, "title": "Cửa sổ ALSC tái sử dụng trong bài toán lập lịch"},
    "fig_ch09": {"page": 74, "top_y": 360, "bottom_y": 1020, "title": "Bố trí nguyên và biến chứng quan hệ tách trong đóng gói 2D"},
    "fig_ch10": {"page": 82, "top_y": 350, "bottom_y": 640, "title": "Cặp nhãn bị cấm và bài toán Antibandwidth trên đồ thị"},
    "fig_ch11": {"page": 88, "top_y": 350, "bottom_y": 540, "title": "Gán nhãn radio khả thi và nén khoảng cấm"},
}

def crop_exact_tikz_diagram(im: Image.Image, top_y: int, bottom_y: int, padding: int = 24) -> Image.Image:
    """Crop the precise TikZ diagram region without any page text paragraphs."""
    width, height = im.size
    
    top = max(0, top_y)
    bottom = min(height, bottom_y)
    
    cropped_page = im.crop((0, top, width, bottom))
    
    # Trim horizontal white background
    bg = Image.new(cropped_page.mode, cropped_page.size, (255, 255, 255))
    diff = ImageChops.difference(cropped_page, bg)
    bbox = diff.getbbox()
    if bbox:
        left = max(0, bbox[0] - padding)
        t_inner = max(0, bbox[1] - padding)
        right = min(cropped_page.width, bbox[2] + padding)
        b_inner = min(cropped_page.height, bbox[3] + padding)
        return cropped_page.crop((left, t_inner, right, b_inner))
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

    with tempfile.TemporaryDirectory(prefix="sat-fig-extract-") as temp_dir:
        for fig_id, meta in EXACT_FIGURE_CROP_MAP.items():
            page_num = meta["page"]
            top_y = meta["top_y"]
            bottom_y = meta["bottom_y"]
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
                trimmed = crop_exact_tikz_diagram(im, top_y, bottom_y)
                
                webp_path = output_dir / f"{fig_id}.webp"
                trimmed.save(webp_path, format="WEBP", quality=95, method=6)
                print(f"[✓] Extracted PRECISE TikZ diagram: {webp_path.name} (page {page_num}, {trimmed.width}x{trimmed.height}px)")

if __name__ == "__main__":
    main()
