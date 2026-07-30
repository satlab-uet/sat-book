#!/usr/bin/env python3

from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

def make_transparent_logo():
    repo_root = Path(__file__).resolve().parent.parent
    src_png = repo_root / "satlab.png"
    img_dir = repo_root / "site" / "assets" / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    if not src_png.exists():
        print("Source satlab.png not found.")
        return

    im = Image.open(src_png).convert("RGBA")
    width, height = im.size

    # The blue emblem circle is centered at (512, 512) with radius ~492.
    center_x, center_y = width / 2, height / 2
    radius = 492

    # High-resolution supersampled circular mask (4x)
    scale = 4
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        [
            (center_x - radius) * scale,
            (center_y - radius) * scale,
            (center_x + radius) * scale,
            (center_y + radius) * scale,
        ],
        fill=255,
    )
    mask = mask.resize((width, height), Image.Resampling.LANCZOS)

    # Cut image inside circle mask
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result.paste(im, (0, 0), mask=mask)

    # Trim empty transparent padding
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)

    # 1. Save main transparent logo
    dest_logo = img_dir / "satlab.png"
    result.save(dest_logo, format="PNG")
    print(f"[✓] Saved transparent logo: {dest_logo} ({result.width}x{result.height}px)")

    # 2. Favicon 32x32
    fav32 = result.resize((32, 32), Image.Resampling.LANCZOS)
    fav32_path = img_dir / "favicon-32.png"
    fav32.save(fav32_path, format="PNG")
    print(f"[✓] Saved transparent favicon-32: {fav32_path}")

    # 3. Favicon.ico
    fav_ico = repo_root / "site" / "favicon.ico"
    fav32.save(fav_ico, format="ICO")
    print(f"[✓] Saved favicon.ico: {fav_ico}")

    # 4. Apple touch icon 180x180
    apple_icon = result.resize((180, 180), Image.Resampling.LANCZOS)
    apple_path = img_dir / "apple-touch-icon.png"
    apple_icon.save(apple_path, format="PNG")
    print(f"[✓] Saved transparent apple touch icon: {apple_path}")

if __name__ == "__main__":
    make_transparent_logo()
