#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

def crop_diagram_content(im: Image.Image) -> Image.Image:
    """
    Remove top header and bottom footer text of LaTeX page,
    keeping only the diagram area in the middle.
    """
    width, height = im.size
    
    # Standard LaTeX page margins: crop top 12% (running head) and bottom 10% (page number)
    top_crop = int(height * 0.10)
    bottom_crop = int(height * 0.90)
    
    cropped_page = im.crop((0, top_crop, width, bottom_crop))
    
    # Trim surrounding white background
    bg = Image.new(cropped_page.mode, cropped_page.size, (255, 255, 255))
    diff = ImageChops.difference(cropped_page, bg)
    bbox = diff.getbbox()
    if bbox:
        padding = 30
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
        print("pdftocairo not found.", file=sys.stderr)
        return

    key_figures = [
        {"id": "fig_ch01", "page": 5, "title": "Sơ đồ vòng lặp CDCL"},
        {"id": "fig_ch03", "page": 17, "title": "Sequential Counter"},
        {"id": "fig_ch04", "page": 25, "title": "Performance Profile"},
        {"id": "fig_ch05", "page": 32, "title": "Shared Counter"},
        {"id": "fig_ch06", "page": 38, "title": "Thanh ghi NSC"},
        {"id": "fig_ch07", "page": 44, "title": "Symmetry Breaking"},
        {"id": "fig_ch08", "page": 54, "title": "ALSC Scheduling"},
        {"id": "fig_ch09", "page": 61, "title": "Đóng gói 2D"},
        {"id": "fig_ch10", "page": 69, "title": "Antibandwidth"},
        {"id": "fig_ch11", "page": 76, "title": "Radio Labeling"},
    ]

    with tempfile.TemporaryDirectory(prefix="sat-crop-") as temp_dir:
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
                print(f"[✓] Cropped exact diagram: {webp_path.name} ({trimmed.width}x{trimmed.height}px)")

if __name__ == "__main__":
    main()
