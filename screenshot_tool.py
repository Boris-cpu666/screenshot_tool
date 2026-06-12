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


def capture_region(*args, **kwargs):
    raise NotImplementedError


def copy_to_clipboard(*args, **kwargs):
    raise NotImplementedError
