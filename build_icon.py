"""Build app icon (256x256) — purple gradient + camera body + screenshot frame.

Run:  python build_icon.py
Output: icon.ico (multi-size: 16/32/48/64/128/256) + icon.png (256x256 preview)
"""
from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def make_icon(size: int) -> Image.Image:
    """Render icon at given size. Returned image is RGBA."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Purple gradient background (rounded square)
    for y in range(size):
        # Gradient: top #6A4FCF → bottom #4A3AA8
        t = y / max(size - 1, 1)
        r = int(0x6A * (1 - t) + 0x4A * t)
        g = int(0x4F * (1 - t) + 0x3A * t)
        b = int(0xCF * (1 - t) + 0xA8 * t)
        d.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Apply rounded corners mask
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    corner = int(size * 0.18)
    md.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=corner, fill=255)
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg.paste(img, (0, 0), mask)
    img = bg
    d = ImageDraw.Draw(img)

    # Camera/screenshot frame: white rounded rect
    pad = int(size * 0.18)
    frame = [pad, pad + int(size * 0.08), size - pad, size - pad]
    corner2 = int(size * 0.08)
    d.rounded_rectangle(frame, radius=corner2, outline=(255, 255, 255, 255), width=max(2, size // 64))

    # Lens: white circle in center
    cx = size // 2
    cy = (frame[1] + frame[3]) // 2 + int(size * 0.02)
    r_lens = int(size * 0.13)
    d.ellipse([cx - r_lens, cy - r_lens, cx + r_lens, cy + r_lens],
              outline=(255, 255, 255, 255), width=max(2, size // 64))

    # Inner lens (purple darker)
    r_in = int(size * 0.06)
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=(0x4A, 0x3A, 0xA8, 255))

    # Flash dot (top-left of frame)
    flash_r = max(2, size // 48)
    d.ellipse([frame[0] + flash_r * 2, frame[1] + flash_r * 2,
               frame[0] + flash_r * 4, frame[1] + flash_r * 4],
              fill=(255, 215, 0, 255))  # gold

    return img


def main() -> None:
    # Preview 256x256 PNG
    big = make_icon(256)
    big.save(os.path.join(OUT_DIR, "icon.png"))

    # Multi-size .ico (Windows 资源管理器 + 任务栏都会用)
    sizes = [16, 32, 48, 64, 128, 256]
    # Pillow ICO: 给一张大图 + sizes 列表，自动 downscale 生成多尺寸 ICO
    big.save(
        os.path.join(OUT_DIR, "icon.ico"),
        format="ICO",
        sizes=[(s, s) for s in sizes],
    )
    print(f"OK: icon.png (256x256) + icon.ico ({', '.join(str(s) for s in sizes)})")


if __name__ == "__main__":
    main()
