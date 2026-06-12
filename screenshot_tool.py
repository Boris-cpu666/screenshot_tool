"""截图小工具：Ctrl+Alt+A 区域截图，存到桌面 + 复制到剪贴板。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image


def save_to_desktop(image: Image.Image) -> Path:
    """把 image 存为 PNG 到桌面，返回完整路径。同秒内冲突加 _2/_3... 后缀。"""
    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    base = f"screenshot_{datetime.now():%Y%m%d_%H%M%S}"
    path = desktop / f"{base}.png"
    suffix = 2
    while path.exists():
        path = desktop / f"{base}_{suffix}.png"
        suffix += 1
    image.save(path, "PNG", optimize=True)
    return path


def capture_region(rect, screen) -> Image.Image:
    """用 mss 截取屏幕上给定矩形（逻辑像素），返回 PIL.Image。"""
    # 逻辑像素 → 物理像素
    scale = screen.devicePixelRatio()
    monitor = {
        "left": int(rect.left() * scale),
        "top": int(rect.top() * scale),
        "width": int(rect.width() * scale),
        "height": int(rect.height() * scale),
    }
    import mss
    with mss.mss() as sct:
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def copy_to_clipboard(*args, **kwargs):
    raise NotImplementedError
