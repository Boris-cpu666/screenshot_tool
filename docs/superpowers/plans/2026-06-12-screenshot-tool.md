# 截图小工具 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Windows 11 上做一个常驻托盘的区域截图小工具：按 `Ctrl+Alt+A` 在屏幕上拖框选区域，松手后自动存为 PNG 到桌面并复制到剪贴板。

**Architecture:** 单进程单文件 Python 工具。Qt 事件循环做主线程（托盘 UI + 透明遮罩 + 截图/保存/剪贴板），`keyboard` 库的 hook 线程捕获全局热键并通过 `Signal` 通知主线程。mss 负责屏幕捕获。3 个纯函数（`capture_region` / `save_to_desktop` / `copy_to_clipboard`）+ 1 个 `ScreenshotOverlay` QWidget + 1 个 `ScreenshotTrayApp` 顶层编排。

**Tech Stack:** Python 3.10+, PyQt5, mss, keyboard, pytest（含 pytest-qt 和 freezegun）

**Spec:** `C:\Users\huang\docs\superpowers\specs\2026-06-12-screenshot-tool-design.md`

---

## 文件结构

把工具建在独立的子目录（不放 Desktop 根目录，避免污染）：

```
C:\Users\huang\Desktop\screenshot_tool\
├── screenshot_tool.py          # 主程序（~200 行）
├── test_screenshot_tool.py     # 单元 + 集成测试
├── requirements.txt            # 依赖
├── README.md                   # 安装 + 使用
├── .gitignore                  # __pycache__, *.pyc, .pytest_cache
└── icon.png                    # 托盘图标（程序运行时生成，32x32 简单图形）
```

每个文件一个职责：
- `screenshot_tool.py` — 所有生产代码（按类 / 函数分段清晰）
- `test_screenshot_tool.py` — 所有测试
- `requirements.txt` / `README.md` / `.gitignore` — 工程文件

子目录里 `git init` 一个独立仓库（用户根目录不是 git repo）。每次 commit 在该子目录里。

---

## Task 1: 项目骨架 + git 初始化

**Files:**
- Create: `C:\Users\huang\Desktop\screenshot_tool\.gitignore`
- Create: `C:\Users\huang\Desktop\screenshot_tool\requirements.txt`
- Create: `C:\Users\huang\Desktop\screenshot_tool\README.md`

- [ ] **Step 1: 创建项目目录**

Run:
```bash
mkdir -p /c/Users/huang/Desktop/screenshot_tool
cd /c/Users/huang/Desktop/screenshot_tool
```
Expected: 目录已创建。

- [ ] **Step 2: 写 .gitignore**

Create `C:\Users\huang\Desktop\screenshot_tool\.gitignore`:

```gitignore
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
.venv/
```

- [ ] **Step 3: 写 requirements.txt**

Create `C:\Users\huang\Desktop\screenshot_tool\requirements.txt`:

```
PyQt5>=5.15
mss>=9.0
keyboard>=0.13
```

测试依赖（可一并放）：

```
-r requirements.txt
pytest>=7.0
pytest-qt>=4.0
freezegun>=1.2
```

最终 `requirements.txt` 应该是 **dev 完整** 的那份（含测试依赖）。生产依赖通过 `pip install PyQt5 mss keyboard` 也行，但为了"一行安装"，用上面这份。

- [ ] **Step 4: 写 README.md（占位）**

Create `C:\Users\huang\Desktop\screenshot_tool\README.md`:

```markdown
# 截图小工具

按 `Ctrl+Alt+A` 区域截图，自动保存到桌面 + 复制到剪贴板。

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python screenshot_tool.py
```

## 退出

托盘右键 → 退出。
```

- [ ] **Step 5: git init 并 commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git init
git add .gitignore requirements.txt README.md
git commit -m "chore: scaffold project"
```
Expected: `git commit` 成功，3 个文件入库。

---

## Task 2: `save_to_desktop` 时间戳文件名（TDD）

**Files:**
- Create: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`
- Create: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`

- [ ] **Step 1: 写测试（time-formatted filename）**

Create `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
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
```

- [ ] **Step 2: 跑测试，确认失败（import error）**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'screenshot_tool'`

- [ ] **Step 3: 写最小实现（仅 save_to_desktop 骨架）**

Create `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`:

```python
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
```

（其他 `capture_region` / `copy_to_clipboard` 占位 import 会因为不存在而失败——先 stub 它们，下一个 task 实装。）

- [ ] **Step 4: stub capture_region + copy_to_clipboard 占位**

Append to `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`（在 `save_to_desktop` 之后）：

```python
def capture_region(*args, **kwargs):
    raise NotImplementedError


def copy_to_clipboard(*args, **kwargs):
    raise NotImplementedError
```

- [ ] **Step 5: 跑测试，确认 save_to_desktop 测试通过**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_save_to_desktop_filename_format -v
```
Expected: PASS

- [ ] **Step 6: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py test_screenshot_tool.py
git commit -m "feat: save_to_desktop with timestamped filename"
```

---

## Task 3: `save_to_desktop` 冲突后缀（TDD）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 写冲突测试**

Append to `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
def test_save_to_desktop_collision_appends_suffix(fake_home):
    """桌面已有同名文件时，新文件应该带 _2 后缀。"""
    with freeze_time("2026-06-12 15:30:22"):
        # 预 touch 一个占用名字的文件
        (fake_home / "Desktop").mkdir(parents=True, exist_ok=True)
        (fake_home / "Desktop" / "screenshot_20260612_153022.png").touch()

        path = save_to_desktop(_one_pixel_image())

    assert path.name == "screenshot_20260612_153022_2.png"
```

- [ ] **Step 2: 跑测试，确认失败**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_save_to_desktop_collision_appends_suffix -v
```
Expected: FAIL — 当前实现会覆盖/重名 OSError（具体错误因 OS 而异，但**测试断言期望 `_2` 后缀，实际得不到**）

- [ ] **Step 3: 修改 save_to_desktop 加冲突检测**

Replace `save_to_desktop` in `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py` with:

```python
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
```

- [ ] **Step 4: 跑测试，确认通过**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_save_to_desktop -v
```
Expected: 2 个 `test_save_to_desktop_*` 测试都 PASS

- [ ] **Step 5: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py test_screenshot_tool.py
git commit -m "feat: save_to_desktop handles filename collisions"
```

---

## Task 4: `save_to_desktop` 目录兜底（TDD）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 写目录兜底测试**

Append to `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
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
```

- [ ] **Step 2: 跑测试，确认已经通过**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_save_to_desktop_falls_back_when_no_desktop -v
```
Expected: **PASS**（Task 3 的 `mkdir(parents=True, exist_ok=True)` 已经处理了）

> 这个 task 主要是**显式覆盖这个边界**——没有新代码。如果你想跳过 commit，可以直接进 Task 5。

- [ ] **Step 3: commit（如需）**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add test_screenshot_tool.py
git commit -m "test: cover save_to_desktop directory fallback"
```

---

## Task 5: `capture_region` 纯函数（TDD）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 写 capture_region 测试（mock mss）**

Append to `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
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
```

- [ ] **Step 2: 跑测试，确认失败（NotImplementedError）**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_capture_region_returns_pil_image -v
```
Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: 实现 capture_region**

Replace the `capture_region` stub in `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py` with:

```python
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
```

注意：顶部的 `import` 需要更新。修改 `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py` 顶部：

```python
"""截图小工具：Ctrl+Alt+A 区域截图，存到桌面 + 复制到剪贴板。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image
```

（`import mss` 留在函数内部，避免在测试 fixture 还没 patch 时 import 出错。）

- [ ] **Step 4: 跑测试，确认通过**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_capture_region_returns_pil_image -v
```
Expected: PASS

- [ ] **Step 5: 跑全部测试，确认没回归**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest -v
```
Expected: 所有测试 PASS

- [ ] **Step 6: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py test_screenshot_tool.py
git commit -m "feat: capture_region with mss and DPI scaling"
```

---

## Task 6: `copy_to_clipboard` 纯函数（TDD）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 写 copy_to_clipboard 测试**

Append to `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
def test_copy_to_clipboard_roundtrip():
    """给定一张图 → 复制到剪贴板 → 读回应该 pixel 相等。"""
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    src = Image.new("RGB", (4, 4), (123, 45, 67))
    copy_to_clipboard(src)

    got_qimage = app.clipboard().image()
    assert not got_qimage.isNull()
    # 拿左上角像素做 spot check
    assert got_qimage.pixel(0, 0) == 0x007B2D43  # QRgb: 0xAARRGGBB
```

> 0x007B2D43 = 0x7B2D43 + alpha=0x00。Qt 用 `#AARRGGBB`。红=0x7B、绿=0x2D、蓝=0x43。

- [ ] **Step 2: 跑测试，确认失败**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_copy_to_clipboard_roundtrip -v
```
Expected: FAIL with `NotImplementedError`

- [ ] **Step 3: 实现 copy_to_clipboard**

Replace the `copy_to_clipboard` stub in `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py` with:

```python
def copy_to_clipboard(image: Image.Image) -> None:
    """把 PIL.Image 复制到 Windows 剪贴板。"""
    from PyQt5.QtGui import QImage
    from PyQt5.QtWidgets import QApplication

    # PIL → QImage（共用内存，不复制）
    img = image.convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)

    QApplication.clipboard().setImage(qimg)
```

- [ ] **Step 4: 跑测试，确认通过**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_copy_to_clipboard_roundtrip -v
```
Expected: PASS

- [ ] **Step 5: 跑全部测试**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest -v
```
Expected: 全部 PASS

- [ ] **Step 6: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py test_screenshot_tool.py
git commit -m "feat: copy_to_clipboard via QClipboard"
```

---

## Task 7: `ScreenshotOverlay` 鼠标拖框 + 信号（TDD）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 写 ScreenshotOverlay 拖框测试**

Append to `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
def test_screenshot_overlay_emits_region_selected(qtbot):
    """模拟鼠标拖框，松手后 region_selected 应 emit 正确的 QRect。"""
    from PyQt5.QtCore import QPoint, Qt
    from PyQt5.QtWidgets import QApplication
    from screenshot_tool import ScreenshotOverlay

    overlay = ScreenshotOverlay()
    qtbot.addWidget(overlay)
    overlay.resize(800, 600)
    overlay.show()
    qtbot.waitExposed(overlay)

    captured = []
    overlay.region_selected.connect(lambda r: captured.append(r))

    start = QPoint(100, 80)
    end = QPoint(300, 250)
    qtbot.mousePress(overlay, Qt.LeftButton, Qt.NoModifier, start)
    qtbot.mouseMove(overlay, end)
    qtbot.mouseRelease(overlay, Qt.LeftButton, Qt.NoModifier, end)

    assert len(captured) == 1
    r = captured[0]
    assert (r.left(), r.top(), r.width(), r.height()) == (100, 80, 200, 170)
```

注意：测试需要 `pytest-qt` 的 `qtbot` fixture。如果你没装，先装：

```bash
pip install pytest-qt
```

并且 pytest-qt 需要一个 `pytest.ini` 里的 `qt_api` 设置，**新建** `C:\Users\huang\Desktop\screenshot_tool\pytest.ini`:

```ini
[pytest]
qt_api=pyqt5
```

- [ ] **Step 2: 跑测试，确认失败（ImportError）**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_screenshot_overlay_emits_region_selected -v
```
Expected: FAIL with `ImportError: cannot import name 'ScreenshotOverlay'`

- [ ] **Step 3: 实现 ScreenshotOverlay 最小版本（仅鼠标拖框，无视觉）**

Append to `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`:

```python
class ScreenshotOverlay(QWidget):
    """全屏半透明遮罩。鼠标拖框，松开后 emit region_selected(QRect)。"""

    region_selected = pyqtSignal(QRect)
    cancelled = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setCursor(Qt.CrossCursor)
        self._start: QPoint | None = None
        self._end: QPoint | None = None
        self._drag_active = False
        self._intentional_close = False  # closeEvent 用

    def start(self) -> None:
        """覆盖所有屏幕并显示。"""
        from PyQt5.QtGui import QGuiApplication
        all_rect = QRect()
        for screen in QGuiApplication.screens():
            all_rect = all_rect.united(screen.geometry())
        self.setGeometry(all_rect)
        self._start = None
        self._end = None
        self._drag_active = False
        self._intentional_close = False
        self.show()
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._start = event.pos()
            self._end = event.pos()
            self._drag_active = True
            self.update()
        elif event.button() == Qt.RightButton:
            # 右键 = 取消（在 start 之后才能触发，QA on right-click 测试覆盖）
            self._intentional_close = True
            self.cancelled.emit()
            self.close()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_active:
            self._end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._drag_active:
            self._drag_active = False
            self._end = event.pos()
            rect = QRect(self._start, self._end).normalized()
            self._intentional_close = True
            if rect.width() > 4 and rect.height() > 4:
                self.region_selected.emit(rect)
            self.close()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self._intentional_close = True
            self.cancelled.emit()
            self.close()

    def closeEvent(self, event) -> None:
        # Alt+F4 等非正常关闭 → 当作取消
        if not self._intentional_close:
            self.cancelled.emit()
        super().closeEvent(event)
```

并在文件顶部增加 import：

```python
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtWidgets import QWidget
```

- [ ] **Step 4: 跑测试，确认通过**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_screenshot_overlay_emits_region_selected -v
```
Expected: PASS

- [ ] **Step 5: 跑全部测试**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest -v
```
Expected: 全部 PASS

- [ ] **Step 6: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py test_screenshot_tool.py pytest.ini
git commit -m "feat: ScreenshotOverlay mouse-drag region selection"
```

---

## Task 8: `ScreenshotOverlay` 取消路径（TDD）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 写取消测试（Esc + 右键）**

Append to `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
def test_screenshot_overlay_esc_cancels(qtbot):
    """按 Esc 应 emit cancelled。"""
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QKeyEvent
    from screenshot_tool import ScreenshotOverlay

    overlay = ScreenshotOverlay()
    qtbot.addWidget(overlay)
    overlay.show()
    qtbot.waitExposed(overlay)

    cancelled = []
    overlay.cancelled.connect(lambda: cancelled.append(True))

    event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
    overlay.keyPressEvent(event)

    assert cancelled == [True]


def test_screenshot_overlay_right_click_cancels(qtbot):
    """鼠标右键应 emit cancelled。"""
    from PyQt5.QtCore import QPoint, Qt
    from screenshot_tool import ScreenshotOverlay

    overlay = ScreenshotOverlay()
    qtbot.addWidget(overlay)
    overlay.show()
    qtbot.waitExposed(overlay)

    cancelled = []
    overlay.cancelled.connect(lambda: cancelled.append(True))

    overlay.mousePressEvent(_FakeMouseEvent(Qt.RightButton, QPoint(50, 50)))

    assert cancelled == [True]
```

需要加一个 `_FakeMouseEvent` helper（QMouseEvent 构造太啰嗦）。Append to test file:

```python
class _FakeMouseEvent:
    """够测试用的 QMouseEvent 替身。"""
    def __init__(self, button, pos):
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QMouseEvent
        # 实际类型必须是 QMouseEvent 才能走 Qt 内部
        self._evt = QMouseEvent(
            QEvent.MouseButtonPress, pos, button, button, Qt.NoModifier
        )

    def button(self):
        return self._evt.button()

    def pos(self):
        return self._evt.pos()
```

> 注：实际更简单——测试里直接调 `overlay.mousePressEvent(真实的_QMouseEvent)`。把 helper 替换成下面这版（去掉 `_FakeMouseEvent`）：

Replace 上面的 `_FakeMouseEvent` 段，**改为**在 `test_screenshot_overlay_right_click_cancels` 内部直接构造：

```python
def test_screenshot_overlay_right_click_cancels(qtbot):
    """鼠标右键应 emit cancelled。"""
    from PyQt5.QtCore import QEvent, QPoint, Qt
    from PyQt5.QtGui import QMouseEvent
    from screenshot_tool import ScreenshotOverlay

    overlay = ScreenshotOverlay()
    qtbot.addWidget(overlay)
    overlay.show()
    qtbot.waitExposed(overlay)

    cancelled = []
    overlay.cancelled.connect(lambda: cancelled.append(True))

    evt = QMouseEvent(
        QEvent.MouseButtonPress,
        QPoint(50, 50),
        Qt.RightButton,
        Qt.RightButton,
        Qt.NoModifier,
    )
    overlay.mousePressEvent(evt)

    assert cancelled == [True]
```

不要写 `_FakeMouseEvent` helper——直接构造 `QMouseEvent`。

- [ ] **Step 2: 跑测试，确认失败**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_screenshot_overlay_esc_cancels test_screenshot_overlay_right_click_cancels -v
```
Expected: FAIL — `cancelled` 是空 list（没绑信号处理逻辑）

- [ ] **Step 3: 实现取消处理**

**无需新增代码**——右键处理已在 Task 7 `mousePressEvent` 里（`elif event.button() == Qt.RightButton` 分支），Esc 处理已在 Task 7 `keyPressEvent` 里。本 task 只负责跑测试 + commit。

- [ ] **Step 4: 跑测试，确认通过**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest -v
```
Expected: 全部 PASS

- [ ] **Step 5: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py test_screenshot_tool.py
git commit -m "feat: ScreenshotOverlay cancel via Esc and right-click"
```

---

## Task 9: `ScreenshotOverlay` 视觉（paintEvent）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

视觉测试需要渲染验证（复杂、价值低），**改为手工验证**——这 task 写实现 + 人工 spot check。

- [ ] **Step 1: 实现 paintEvent**

Add to `ScreenshotOverlay` in `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`（在 `mouseMoveEvent` 后）：

```python
    def paintEvent(self, event) -> None:
        from PyQt5.QtGui import QColor, QPainter, QPen

        painter = QPainter(self)
        # 整屏半透明黑
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))

        if self._start is not None and self._end is not None:
            rect = QRect(self._start, self._end).normalized()
            # 挖空：清掉选区的填充
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            # 红边框
            pen = QPen(QColor(255, 0, 0), 1)
            painter.setPen(pen)
            painter.drawRect(rect)
        painter.end()
```

并在 `__init__` 顶部加（确保 `WA_NoSystemBackground` 配合 translucent 正确渲染）：

```python
        self.setAttribute(Qt.WA_NoSystemBackground, True)
```

- [ ] **Step 2: 跑全部测试**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest -v
```
Expected: 全部 PASS（paintEvent 不应破坏信号测试）

- [ ] **Step 3: 手工 spot-check（手动验证）**

为了**不打断 TDD 节奏**，这一节给一个独立的 `manual_check.py` 脚本。**新建** `C:\Users\huang\Desktop\screenshot_tool\manual_check.py`:

```python
"""手工验证 ScreenshotOverlay 视觉：跑起来后用鼠标拖框，目视检查。"""
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from screenshot_tool import ScreenshotOverlay


if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ScreenshotOverlay()
    overlay.start()
    overlay.region_selected.connect(lambda r: print(f"SELECTED: {r}"))
    overlay.cancelled.connect(lambda: print("CANCELLED"))
    sys.exit(app.exec_())
```

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python manual_check.py
```

**人工验证清单**（全部勾选才算 OK）：
- [ ] 屏幕变暗（半透明黑）
- [ ] 鼠标变十字
- [ ] 拖框时：选区**透出原内容**（"挖空"效果）
- [ ] 选区边框是红色 1px
- [ ] 松手后选区信号打印到 console
- [ ] 按 Esc 取消，打印 "CANCELLED"
- [ ] 鼠标右键取消，打印 "CANCELLED"

任何一项不通过，回去调 paintEvent 的 QColor alpha / CompositionMode。

- [ ] **Step 4: commit（实现 + manual_check 脚本）**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py manual_check.py
git commit -m "feat: ScreenshotOverlay visual rendering (paintEvent)"
```

> 决定 `manual_check.py` 是否入仓：暂时入仓（方便回归），如果觉得脏也可以 `.gitignore` 掉。

---

## Task 10: `ScreenshotTrayApp` 编排（集成测试 + 真实实现）

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 写集成测试（mock 掉所有 IO）**

Append to `C:\Users\huang\Desktop\screenshot_tool\test_screenshot_tool.py`:

```python
def test_tray_app_full_flow(monkeypatch, fake_home, qtbot):
    """on_hotkey → 选区 → capture → save → clipboard → notify 整链路。

    替换 capture_region / save_to_desktop / copy_to_clipboard / 托盘通知，
    验证 ScreenshotTrayApp 把它们正确串起来。
    """
    from PyQt5.QtCore import QRect
    from PyQt5.QtWidgets import QApplication
    from screenshot_tool import ScreenshotTrayApp

    # 关键：避免在测试中真注册全局热键钩子污染当前 Windows session
    monkeypatch.setattr("keyboard.add_hotkey", lambda *a, **kw: None)
    monkeypatch.setattr("keyboard.unhook_all", lambda: None)

    captured = []
    saved = []
    copied = []
    notified = []

    monkeypatch.setattr(
        "screenshot_tool.capture_region",
        lambda rect, screen: (captured.append(rect) or _one_pixel_image()),
    )
    monkeypatch.setattr(
        "screenshot_tool.save_to_desktop",
        lambda img: (saved.append(img) or fake_home / "fake.png"),
    )
    monkeypatch.setattr(
        "screenshot_tool.copy_to_clipboard",
        lambda img: copied.append(img),
    )

    app = ScreenshotTrayApp()
    monkeypatch.setattr(
        app._tray, "showMessage",
        lambda *a, **kw: notified.append(a),
    )

    # 直接调 on_hotkey（绕过真实 keyboard hook）
    app.on_hotkey()
    qtbot.waitUntil(lambda: app._overlay is not None, timeout=2000)

    # 模拟选区 emit
    test_rect = QRect(10, 20, 300, 200)
    app._overlay.region_selected.emit(test_rect)
    qtbot.waitUntil(lambda: bool(saved), timeout=2000)

    assert captured == [test_rect]
    assert len(saved) == 1
    assert len(copied) == 1
    assert len(notified) == 1
    # 通知消息应该提到文件路径
    assert "fake.png" in notified[0][1]
```

- [ ] **Step 2: 跑测试，确认失败**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_tray_app_full_flow -v
```
Expected: FAIL with `ImportError: cannot import name 'ScreenshotTrayApp'`

- [ ] **Step 3: 实现 ScreenshotTrayApp**

Append to `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`:

```python
class ScreenshotTrayApp:
    """顶层编排：托盘 + 全局热键 + 区域选择 + 截图链路。"""

    # 跨线程信号：keyboard hook 线程 → Qt 主线程
    _hotkey_pressed = pyqtSignal()

    def __init__(self) -> None:
        from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon

        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("系统托盘不可用，本程序无法运行。")

        # 托盘图标（占位：生成一个简单 32x32 PNG）
        self._tray = QSystemTrayIcon(self._make_icon())
        self._tray.setToolTip("截图小工具 (Ctrl+Alt+A)")

        # 右键菜单
        menu = QMenu()
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        self._tray.setContextMenu(menu)
        self._tray.show()

        # 跨线程：keyboard 库在 hook 线程触发，pyqtSignal 自动 QueuedConnection
        self._hotkey_pressed.connect(self.on_hotkey)

        # 全局热键
        import keyboard
        keyboard.add_hotkey("ctrl+alt+a", lambda: self._hotkey_pressed.emit())

        # 状态
        self._overlay: ScreenshotOverlay | None = None
        self._overlay_active = False

    @staticmethod
    def _make_icon():
        from PyQt5.QtCore import QSize
        from PyQt5.QtGui import QColor, QIcon, QImage, QPainter, QPixmap
        img = QImage(QSize(32, 32), QImage.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(70, 130, 200))
        p.setPen(QColor(255, 255, 255))
        p.drawRoundedRect(2, 4, 28, 24, 3, 3)
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(8, 9, 6, 6)
        p.drawEllipse(18, 9, 6, 6)
        p.end()
        return QIcon(QPixmap.fromImage(img))

    def on_hotkey(self) -> None:
        """主线程：启动 overlay。"""
        if self._overlay_active:
            return
        self._overlay_active = True
        self._overlay = ScreenshotOverlay()
        self._overlay.region_selected.connect(self._on_region_selected)
        self._overlay.cancelled.connect(self._on_cancelled)
        self._overlay.start()

    def _on_region_selected(self, rect) -> None:
        from PyQt5.QtGui import QGuiApplication
        from PyQt5.QtWidgets import QSystemTrayIcon
        screen = QGuiApplication.primaryScreen()
        image = capture_region(rect, screen)
        path = save_to_desktop(image)
        copy_to_clipboard(image)
        self._tray.showMessage(
            "截图已保存",
            f"桌面\\{path.name}\n（已复制到剪贴板）",
            QSystemTrayIcon.Information,
            3000,
        )
        self._cleanup_overlay()

    def _on_cancelled(self) -> None:
        self._cleanup_overlay()

    def _cleanup_overlay(self) -> None:
        if self._overlay is not None:
            self._overlay.deleteLater()
            self._overlay = None
        self._overlay_active = False
```

并在文件顶部 import 段加：

```python
from PyQt5.QtGui import QPixmap, QSystemTrayIcon  # noqa: F401  — 实际 import 在类内
```

> 实际 `QSystemTrayIcon` 已在类内 import，**不需要顶部加**。这步跳过。

- [ ] **Step 4: 跑测试**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest test_screenshot_tool.py::test_tray_app_full_flow -v
```
Expected: PASS

- [ ] **Step 5: 跑全部测试**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest -v
```
Expected: 全部 PASS

- [ ] **Step 6: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py test_screenshot_tool.py
git commit -m "feat: ScreenshotTrayApp orchestrator"
```

---

## Task 11: main 入口 + 关闭清理

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`

- [ ] **Step 1: 在文件末尾加 main 块**

Append to `C:\Users\huang\Desktop\screenshot_tool\screenshot_tool.py`:

```python
def main() -> int:
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 托盘常驻，关闭遮罩不退出
    tray_app = ScreenshotTrayApp()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: smoke 启动（手工）**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && timeout 3 python screenshot_tool.py; echo "exit=$?"
```
Expected: 进程启动 → 托盘出现 → 3 秒后 timeout 强杀

> 用 timeout 3 是因为 `app.exec_()` 不会自己退出。如果 timeout 不可用，改为手动 Ctrl+C。

- [ ] **Step 3: commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add screenshot_tool.py
git commit -m "feat: main entry point with system tray"
```

---

## Task 12: README 完善 + 最终验证

**Files:**
- Modify: `C:\Users\huang\Desktop\screenshot_tool\README.md`

- [ ] **Step 1: 写完整 README**

Replace `C:\Users\huang\Desktop\screenshot_tool\README.md` with:

````markdown
# 截图小工具

Windows 11 上的轻量区域截图工具。`Ctrl+Alt+A` 区域截图，存到桌面 + 复制到剪贴板。

## 功能

- 全局快捷键 `Ctrl+Alt+A` 触发
- 鼠标拖框选区域（`Esc` 或右键取消）
- 截图自动保存为 `screenshot_YYYYMMDD_HHMMSS.png` 到桌面
- 截图自动复制到剪贴板
- 系统托盘常驻，右键 → 退出
- 多显示器支持

## 安装

```bash
pip install -r requirements.txt
```

需要 Python 3.10+。

## 运行

```bash
python screenshot_tool.py
```

托盘出现后，按 `Ctrl+Alt+A` 即可截图。

## 退出

托盘图标 → 右键 → 退出。

## 测试

```bash
python -m pytest -v
```

## 常见问题

**Q: 提示"快捷键被占用"？**
A: 改用其他软件的全局快捷键设置释放 `Ctrl+Alt+A`，或修改 `screenshot_tool.py` 里 `keyboard.add_hotkey` 的第一个参数。

**Q: 截图区域不对？**
A: 多 DPI 缩放下，按逻辑像素选区，物理像素截屏——已处理。如有偏差请报 issue 带屏幕缩放比例。
````

- [ ] **Step 2: 跑最终全测**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && python -m pytest -v
```
Expected: 全部 PASS

- [ ] **Step 3: 最终 commit**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool
git add README.md
git commit -m "docs: comprehensive README"
```

- [ ] **Step 4: 看一眼 git log**

Run:
```bash
cd /c/Users/huang/Desktop/screenshot_tool && git log --oneline
```
Expected: 看到 9–10 个 commit，每个对应一个 task

---

## Self-Review Checklist（执行后核对）

- [ ] 所有 12 个 task 完成
- [ ] `pytest -v` 全部 PASS
- [ ] `python screenshot_tool.py` 启动正常、托盘可见
- [ ] 手工验证：按 `Ctrl+Alt+A` 选区 → 松手 → 桌面有 PNG + 剪贴板有图
- [ ] 手工验证：按 `Esc` / 右键 能取消
- [ ] 手工验证：托盘 → 退出 能正常关闭进程
- [ ] git log 干净、commit message 简洁
