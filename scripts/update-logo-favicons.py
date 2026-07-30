#!/usr/bin/env python3

from pathlib import Path
from PIL import Image

def main():
    repo_root = Path(__file__).resolve().parent.parent
    src_png = repo_root / "satlab.png"
    img_dir = repo_root / "site" / "assets" / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    if not src_png.exists():
        print(f"Error: {src_png} not found.")
        return

    im = Image.open(src_png).convert("RGBA")
    
    # 1. Copy main logo png
    dest_logo = img_dir / "satlab.png"
    im.save(dest_logo, format="PNG", optimize=True)
    print(f"[✓] Saved logo: {dest_logo}")

    # 2. Favicon 32x32
    fav32 = im.resize((32, 32), Image.Resampling.LANCZOS)
    fav32_path = img_dir / "favicon-32.png"
    fav32.save(fav32_path, format="PNG")
    print(f"[✓] Saved favicon: {fav32_path}")

    # 3. Apple touch icon 180x180
    apple_icon = im.resize((180, 180), Image.Resampling.LANCZOS)
    apple_path = img_dir / "apple-touch-icon.png"
    apple_icon.save(apple_path, format="PNG")
    print(f"[✓] Saved apple touch icon: {apple_path}")

if __name__ == "__main__":
    main()
