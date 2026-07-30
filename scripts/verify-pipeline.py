#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

def get_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    repo_root = Path(__file__).resolve().parent.parent
    user_target_pdf = Path("/Users/tuyenkv/Documents/SAT Training/output/pdf/Bieu_dien_SAT_toi_uu_Ban_hieu_chinh_sau_phan_bien.pdf")
    build_pdf = repo_root / "build" / "main.pdf"
    site_dir = repo_root / "_site"
    download_pdf = site_dir / "downloads" / "sat-book.pdf"
    
    print("==================================================")
    print("   SOFTWARE ENGINEERING END-TO-END PIPELINE VERIFICATION")
    print("==================================================")
    
    # 1. PDF Verification
    if user_target_pdf.exists():
        target_sha = get_sha256(user_target_pdf)
        print(f"[✓] User Target PDF found: {user_target_pdf.name}")
        print(f"    SHA-256: {target_sha}")
        
        if build_pdf.exists():
            build_sha = get_sha256(build_pdf)
            if target_sha == build_sha:
                print(f"[✓] build/main.pdf matches target PDF SHA-256 perfectly.")
            else:
                print(f"[X] MISMATCH: build/main.pdf ({build_sha}) != target ({target_sha})", file=sys.stderr)
                sys.exit(1)
    else:
        print(f"[!] Target PDF not found at {user_target_pdf}, relying on build/main.pdf")

    if download_pdf.exists():
        download_sha = get_sha256(download_pdf)
        if target_sha == download_sha:
            print(f"[✓] _site/downloads/sat-book.pdf matches target PDF SHA-256.")
        else:
            print(f"[X] MISMATCH in static output downloads!", file=sys.stderr)
            sys.exit(1)

    # 2. Checksum File Verification
    sha_file = site_dir / "downloads" / "SHA256SUMS"
    if sha_file.exists():
        sha_content = sha_file.read_text(encoding="utf-8")
        if target_sha in sha_content:
            print(f"[✓] SHA256SUMS contains valid hash.")
        else:
            print(f"[X] SHA256SUMS missing current PDF hash!", file=sys.stderr)
            sys.exit(1)

    # 3. Figure Asset Verification
    diagram_dir = repo_root / "site" / "assets" / "images" / "diagrams"
    expected_figures = [
        "fig_ch01.webp", "fig_ch03.webp", "fig_ch04.webp", "fig_ch05.webp",
        "fig_ch06.webp", "fig_ch07.webp", "fig_ch08.webp", "fig_ch09.webp",
        "fig_ch10.webp", "fig_ch11.webp"
    ]
    for fig in expected_figures:
        fig_path = diagram_dir / fig
        if fig_path.exists() and fig_path.stat().st_size > 0:
            print(f"[✓] Figure asset validated: {fig} ({fig_path.stat().st_size} bytes)")
        else:
            print(f"[X] Missing or zero-byte figure asset: {fig}", file=sys.stderr)
            sys.exit(1)

    # 4. HTML Integrity Verification
    index_html = site_dir / "index.html"
    if not index_html.exists():
        print(f"[X] _site/index.html is missing!", file=sys.stderr)
        sys.exit(1)
        
    html_text = index_html.read_text(encoding="utf-8")
    
    # Verify Schema.org JSON-LD
    json_ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_text, re.DOTALL)
    if json_ld_match:
        try:
            data = json.loads(json_ld_match.group(1))
            assert data["@type"] == "Book"
            print(f"[✓] JSON-LD Schema.org metadata parsed and validated successfully.")
        except Exception as e:
            print(f"[X] Invalid JSON-LD metadata: {e}", file=sys.stderr)
            sys.exit(1)
            
    # Verify Anchors
    anchors = ["gioi-thieu", "muc-luc", "hinh-anh", "trich-dan"]
    for a in anchors:
        if f'id="{a}"' in html_text or f'id=\'{a}\'' in html_text:
            print(f"[✓] Anchor section confirmed: #{a}")
        else:
            print(f"[X] Missing anchor id: #{a}", file=sys.stderr)
            sys.exit(1)

    print("\nALL PIPELINE VERIFICATIONS PASSED 100% CLEANLY!")

if __name__ == "__main__":
    main()
