#!/usr/bin/env python3

from __future__ import annotations

import glob
import os
import re
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

HEADER = r"""\documentclass[tikz,margin=10pt]{standalone}
\usepackage{fontspec}
\setmainfont{Libertinus Serif}
\setsansfont{Libertinus Serif}
\usepackage{amsmath,amssymb,xcolor}
\usepackage{tikz}
\usetikzlibrary{
  arrows.meta,
  positioning,
  calc,
  fit,
  matrix,
  shapes.geometric,
  decorations.pathreplacing,
  backgrounds
}

\definecolor{Ink}{HTML}{000000}
\definecolor{Blue}{HTML}{1769AA}
\definecolor{Teal}{HTML}{197278}
\definecolor{Gold}{HTML}{B7791F}
\definecolor{Rule}{HTML}{CBD5DC}
\definecolor{PaleBlue}{HTML}{F1F6FA}
\definecolor{PaleTeal}{HTML}{F0F7F6}
\definecolor{PaleGold}{HTML}{FFF8E7}
\definecolor{SoftGray}{HTML}{F6F7F8}

\tikzset{
  satfig/.style={font=\rmfamily\small,>=Stealth,node distance=8mm and 12mm},
  satbox/.style={draw=black,thick,fill=white,rounded corners=2pt,inner sep=6pt,align=center,font=\rmfamily\small},
  satedge/.style={draw=black,->,thick},
  satnode/.style={circle,draw=black,thick,inner sep=2pt,minimum size=6mm,font=\rmfamily\small},
  satlabel/.style={font=\rmfamily\tiny\color{black}}
}
\begin{document}
"""
FOOTER = r"\end{document}"

def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "site" / "assets" / "images" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(str(repo_root / "book" / "chapters" / "*.tex")))
    fig_count = 0
    rendered_count = 0

    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            text = fp.read()
        
        figures = re.findall(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", text, re.DOTALL)
        for fig in figures:
            fig_count += 1
            label_m = re.search(r"\\label\{([^}]+)\}", fig)
            label = label_m.group(1) if label_m else f"fig_{fig_count}"
            label_clean = label.replace(":", "_").replace("-", "_")
            
            tikz_m = re.search(r"(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})", fig, re.DOTALL)
            if not tikz_m:
                continue
            
            tikz_code = tikz_m.group(1)
            tex_content = HEADER + tikz_code + FOOTER
            
            with tempfile.TemporaryDirectory(prefix="sat-fig-") as tmpdir:
                tmp_tex = Path(tmpdir) / "diag.tex"
                tmp_tex.write_text(tex_content, encoding="utf-8")
                
                res = subprocess.run(
                    ["lualatex", "-interaction=nonstopmode", "diag.tex"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True
                )
                
                diag_pdf = Path(tmpdir) / "diag.pdf"
                if diag_pdf.exists():
                    out_png_prefix = Path(tmpdir) / label_clean
                    subprocess.run([
                        "pdftocairo", "-singlefile", "-png", "-r", "300",
                        str(diag_pdf), str(out_png_prefix)
                    ], check=True)
                    
                    png_file = Path(tmpdir) / f"{label_clean}.png"
                    if png_file.exists():
                        im = Image.open(png_file).convert("RGB")
                        bg = Image.new("RGB", im.size, (255, 255, 255))
                        diff = ImageChops.difference(im, bg)
                        bbox = diff.getbbox()
                        if bbox:
                            pad = 12
                            left = max(0, bbox[0] - pad)
                            top = max(0, bbox[1] - pad)
                            right = min(im.width, bbox[2] + pad)
                            bottom = min(im.height, bbox[3] + pad)
                            im = im.crop((left, top, right, bottom))
                        
                        webp_path = output_dir / f"{label_clean}.webp"
                        im.save(webp_path, format="WEBP", quality=95, method=6)
                        rendered_count += 1
                        print(f"[✓] Extracted TikZ diagram: {label_clean}.webp ({im.width}x{im.height}px)")
                else:
                    print(f"[X] Failed to compile TikZ diagram for {label}", file=sys.stderr)

    print(f"\n[✓] Rendered {rendered_count}/{fig_count} TikZ diagrams into {output_dir}")

if __name__ == "__main__":
    main()
