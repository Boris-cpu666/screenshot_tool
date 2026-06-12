"""截图小工具：Ctrl+Alt+A 区域截图，存到桌面 + 复制到剪贴板。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget


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
        # mss.Shot.bgra is BGRX (4 bytes/pixel, X = padding). PIL's "raw" decoder
        # with "BGRX" args converts BGRX → RGB, ignoring the X channel.
        return Image.frombytes("RGB", shot.size, bytes(shot.bgra), "raw", "BGRX")


def copy_to_clipboard(image: Image.Image) -> None:
    """把 PIL.Image 复制到 Windows 剪贴板。"""
    from PyQt5.QtGui import QImage
    from PyQt5.QtWidgets import QApplication

    # PIL → QImage（共用内存，不复制）
    img = image.convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)

    QApplication.clipboard().setImage(qimg)


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
            # 右键 = 取消
            self._intentional_close = True
            self.cancelled.emit()
            self.close()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_active:
            self._end = event.pos()
            self.update()

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


class ScreenshotTrayApp(QObject):
    """顶层编排：托盘 + 全局热键 + 区域选择 + 截图链路。"""

    # 跨线程信号：keyboard hook 线程 → Qt 主线程
    _hotkey_pressed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
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
