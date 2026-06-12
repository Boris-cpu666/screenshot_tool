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
