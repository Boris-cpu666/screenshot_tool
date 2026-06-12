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
