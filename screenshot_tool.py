"""截图小工具：Ctrl+Alt+A 区域截图，存到桌面 + 复制到剪贴板。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image


def save_to_desktop(image: Image.Image) -> Path:
    """把 image 存为 PNG 到桌面，返回完整路径。"""
    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    name = f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
    path = desktop / name
    image.save(path, "PNG", optimize=True)
    return path


def capture_region(*args, **kwargs):
    raise NotImplementedError


def copy_to_clipboard(*args, **kwargs):
    raise NotImplementedError
