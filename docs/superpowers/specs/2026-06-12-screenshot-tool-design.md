# 截图小工具 — 设计文档

- **日期**：2026-06-12
- **方案**：MVP（方案 A）
- **平台**：Windows 11
- **状态**：设计已批准，待进入实现

## 1. 概述

一个常驻系统托盘的 Windows 截图工具。全局快捷键 `Ctrl+Alt+A` 触发区域选择截图，截下后自动保存到桌面（PNG）并复制到剪贴板。

## 2. 决策汇总

| 维度 | 决策 |
|------|------|
| 截图范围 | 区域选择（鼠标拖框） |
| 技术栈 | Python + PyQt5 + mss + keyboard |
| 快捷键 | `Ctrl+Alt+A` |
| 文件名 | `screenshot_YYYYMMDD_HHMMSS.png` |
| 文件格式 | PNG（无损） |
| 保存目录 | `~/Desktop/`（不存在时兜底 `~/`） |
| 剪贴板 | 每次截图自动复制到剪贴板 |
| 启动 | `python screenshot_tool.py` |
| 退出 | 托盘右键 → 退出 |
| 取消 | `Esc` 键 或 鼠标右键 |
| 依赖 | `pip install PyQt5 mss keyboard` |

## 3. 架构

### 3.1 文件结构

```
Desktop/
└── screenshot_tool.py          # 主程序（约 150–200 行）
test_screenshot_tool.py         # 单元测试（pytest）
README.md                       # 安装和使用说明
```

### 3.2 单进程模型

- **主线程**：Qt 事件循环、托盘 UI、截图/保存/剪贴板
- **键盘 hook 线程**（`keyboard` 库自带）：捕获 `Ctrl+Alt+A`，通过 `Signal` 通知主线程（`Qt.QueuedConnection`）
- **mss 截图调用**在主线程同步执行（亚毫秒级，无须线程化）

### 3.3 依赖选型理由

| 库 | 为什么是它 |
|----|-----------|
| **PyQt5** | `QWidget + WA_TranslucentBackground + WindowStaysOnTopHint` 是 Windows 上做"全屏透明遮罩 + 鼠标拖框"最稳的方式；自带 `QSystemTrayIcon` |
| **mss** | 比 `PIL.ImageGrab` 快；`mss.monitors` 一次拿到所有屏幕的 bbox，天然多显示器 |
| **keyboard** | 全局热键最简的 Python 库；用户级 hook，免管理员权限 |

## 4. 关键单元

5 个最小单元。前 3 个是纯函数（无 PyQt 状态、可独立测试），后 2 个是 GUI 编排。

| # | 单元 | 类型 | 职责 |
|---|------|------|------|
| 1 | `ScreenshotOverlay(QWidget)` | Qt Widget | 全屏透明遮罩 + 鼠标拖框 + Esc/右键取消 |
| 2 | `capture_region(rect)` | 纯函数 | 给定屏幕坐标矩形，用 mss 截屏返回 `PIL.Image` |
| 3 | `save_to_desktop(image)` | 纯函数 | 生成时间戳文件名，存为 PNG，返回完整 `Path` |
| 4 | `copy_to_clipboard(image)` | 纯函数 | 把 PIL 图塞进 Windows 剪贴板（`QClipboard.setImage`） |
| 5 | `ScreenshotTrayApp` | QApplication 编排 | 启动托盘、注册热键、把 1–4 串起来 |

### 4.1 单元签名

```python
def capture_region(rect: QRect, screen: QScreen) -> PIL.Image: ...
def save_to_desktop(image: PIL.Image) -> Path: ...
def copy_to_clipboard(image: PIL.Image) -> None: ...

class ScreenshotOverlay(QWidget):
    region_selected = pyqtSignal(QRect)
    cancelled = pyqtSignal()

class ScreenshotTrayApp:
    def __init__(self) -> None: ...
    def on_hotkey(self) -> None: ...
    def on_region_selected(self, rect: QRect) -> None: ...
```

## 5. 数据流（一次截图端到端）

```
T0  keyboard hook 线程捕获 ctrl+alt+a
     └─ Signal emit 到主线程（Qt.QueuedConnection）

T1  主线程: ScreenshotTrayApp.on_hotkey()
     └─ 实例化 ScreenshotOverlay
     └─ setGeometry(覆盖所有屏幕并集 bbox，mss.monitors 算出)
     └─ show() + raise_() + activateWindow()
     └─ 鼠标 cursor 改十字

T2  鼠标按下: self.start = event.pos()
T3  鼠标移动: self.end = event.pos() → update() → paintEvent 画半透明黑遮罩 + 挖空选区 + 红边框
T4  鼠标松开: 校验 width>4 且 height>4
     ├─ 太小 → 忽略
     └─ 正常 → emit region_selected(QRect)

T5  overlay.close()
T6  capture_region(rect) → PIL.Image
T7  顺序执行（均在主线程，亚毫秒级）：
     ├─ save_to_desktop(img) → Path
     └─ copy_to_clipboard(img)
T8  tray.showMessage("截图已保存", "桌面\\xxx.png\n（已复制到剪贴板）", msecs=3000)
T9  回到托盘常驻，等待下一次快捷键
```

### 5.1 取消路径

- `Esc` 键 → overlay `keyPressEvent` → `emit cancelled()` → `overlay.close()`，无副作用
- 鼠标右键 → overlay `contextMenuEvent` → 同上
- 遮罩打开期间 `Ctrl+Alt+A` 被按 → 忽略（防自激）：`ScreenshotTrayApp` 维护 `self._overlay_active: bool`，`on_hotkey` 入口先 `if self._overlay_active: return`

### 5.2 DPI 缩放

- 选区按**逻辑像素**记录
- mss 截**物理像素**
- 转换用 `QScreen.devicePixelRatio()`

## 6. 错误处理

| 场景 | 行为 |
|------|------|
| 桌面目录不存在 | 兜底 `Path.home() / "Desktop"`，仍失败则 `Path.home()`；启动时 `mkdir(parents=True, exist_ok=True)` |
| 文件名冲突（同秒连按） | 加 `_2`、`_3` … 后缀 |
| 用户选区太小（< 5×5 px） | 视为误点，忽略，不保存 |
| mss 抛错 | tray 报错气泡，不崩进程 |
| PIL/PyQt5 import 失败 | fail-fast，顶部不 try |
| 无托盘系统 | 启动时 `QSystemTrayIcon.isSystemTrayAvailable()` 检查 |
| 快捷键被其他程序独占 | 启动时 `keyboard.add_hotkey` 抛 `ValueError` → 弹消息框 |
| 遮罩被 Alt+F4 等意外关闭 | override `closeEvent` 拦截非正常路径 |

## 7. 测试

MVP 范围内不写 UI 测试（PyQt 测试 setup 太重），**纯函数全单元测**：

| 测试目标 | 怎么测 |
|----------|--------|
| `save_to_desktop` 文件名生成 | `freezegun` 固定 datetime → 断言文件名 |
| `save_to_desktop` 冲突后缀 | 预先 `touch` 同时间戳文件 → 断言带 `_2` |
| `save_to_desktop` 目录兜底 | 临时改 `HOME` env 指向无 Desktop 的目录 |
| `capture_region` | `unittest.mock.patch("mss.mss")` 给定固定 bytes → 断言 Image |
| `copy_to_clipboard` | `QApplication.clipboard().image()` 读回对比 |
| `ScreenshotOverlay` 信号 | `QTest.mousePress/Move/Release` 断言 `region_selected` emit 的 QRect |

测试文件：`test_screenshot_tool.py`，跑 `pytest`。

## 8. 范围外（MVP 明确不做）

- 截图标注（框、箭头、马赛克、文字） → 后续功能
- 选区宽高实时显示 → 后续功能
- 历史记录 / 回看 → 后续功能
- 开机自启 → 单独 issue
- 多快捷键（全屏/窗口/区域） → 后续功能
- JPG / WebP 输出 → 后续功能

## 9. 启动与退出

- **启动**：`python screenshot_tool.py`（命令行或双击 .py 关联）
- **进程生命周期**：常驻托盘，不主动退出
- **退出方式**：托盘右键菜单 → 退出

## 10. 安装

```bash
pip install PyQt5 mss keyboard
```

`keyboard` 在 Windows 上使用 `WH_KEYBOARD_LL` 钩子（用户级），多数情况不需要管理员权限即可工作。
