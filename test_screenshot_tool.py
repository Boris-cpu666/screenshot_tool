"""Tests for screenshot_tool."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from PIL import Image

from screenshot_tool import save_to_desktop, capture_region, copy_to_clipboard


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """Point HOME at a temp dir; return the temp dir."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    return tmp_path


def _one_pixel_image() -> Image.Image:
    return Image.new("RGB", (1, 1), (255, 0, 0))


def test_save_to_desktop_filename_format(fake_home):
    """给定固定时间，文件名应该是 screenshot_YYYYMMDD_HHMMSS.png。"""
    with freeze_time("2026-06-12 15:30:22"):
        path = save_to_desktop(_one_pixel_image())

    assert path.name == "screenshot_20260612_153022.png"
    assert path.parent.name == "Desktop"


def test_save_to_desktop_collision_appends_suffix(fake_home):
    """桌面已有同名文件时，新文件应该带 _2 后缀。"""
    with freeze_time("2026-06-12 15:30:22"):
        # 预 touch 一个占用名字的文件
        (fake_home / "Desktop").mkdir(parents=True, exist_ok=True)
        (fake_home / "Desktop" / "screenshot_20260612_153022.png").touch()

        path = save_to_desktop(_one_pixel_image())

    assert path.name == "screenshot_20260612_153022_2.png"


def test_save_to_desktop_falls_back_when_no_desktop(tmp_path, monkeypatch):
    """HOME 下没有 Desktop 目录时，应自动创建；仍失败则降级到 HOME。"""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    # 不创建 Desktop/，save_to_desktop 应该自己 mkdir

    with freeze_time("2026-06-12 15:30:22"):
        path = save_to_desktop(_one_pixel_image())

    assert path.name == "screenshot_20260612_153022.png"
    assert path.parent.exists()
    assert path.parent.is_dir()


def test_capture_region_returns_pil_image(monkeypatch):
    """capture_region 应该用 mss 在给定矩形上截图，返回 PIL.Image。"""
    from PyQt5.QtCore import QRect
    from PyQt5.QtGui import QGuiApplication

    # 给一个 RGB 2x2 的 raw bytes
    raw_bytes = bytes([255, 0, 0,   0, 255, 0,
                       0, 0, 255,   255, 255, 255])

    class _FakeSCT:
        def __init__(self): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def grab(self, monitor):
            # 校验传给 mss 的矩形坐标
            assert monitor == {"left": 0, "top": 0, "width": 2, "height": 2}
            from mss.tools import to_png  # 仅供 mock
            class _Shot:
                def __init__(self, raw, size):
                    self.rgb = raw
                    self.size = size
            return _Shot(raw_bytes, (2, 2))

    monkeypatch.setattr("mss.mss", lambda: _FakeSCT())

    # capture_region 需要 QScreen，从 QGuiApplication 拿
    app = QGuiApplication.instance() or QGuiApplication([])
    screen = app.primaryScreen()

    img = capture_region(QRect(0, 0, 2, 2), screen)

    assert isinstance(img, Image.Image)
    assert img.size == (2, 2)
    assert img.mode == "RGB"
