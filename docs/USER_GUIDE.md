# 截图小工具 — 用户手册

> 完整中文使用手册。功能、快捷键、自定义、技巧、常见问题。

## 目录

- [快速开始](#快速开始)
- [功能详解](#功能详解)
- [快捷键与鼠标](#快捷键与鼠标)
- [截图文件管理](#截图文件管理)
- [自定义与进阶](#自定义与进阶)
- [常见问题](#常见问题)
- [使用技巧](#使用技巧)
- [卸载](#卸载)

---

## 快速开始

1. **启动**：双击 `screenshot_tool.exe`（安装版）或桌面"截图小工具"快捷方式
2. **看到托盘图标**：右下角系统托盘出现紫色相机图标 = 启动成功
3. **截图**：按 `Ctrl+Alt+A` → 屏幕变暗 → 拖鼠标选区域 → 松手
4. **取消**：选区时按 `Esc` 或鼠标右键
5. **退出**：托盘图标 → 右键 → 退出

---

## 功能详解

### 区域截图

- **触发**：全局快捷键 `Ctrl+Alt+A`（任何应用下都响应）
- **视觉反馈**：
  - 屏幕覆盖一层**半透明黑色遮罩**（约 31% 不透明）
  - 鼠标变**十字光标**
  - 拖框时选区**"挖空"**显示原内容（你可以透过选区看到要截的图）
  - 选区**红边框** 1px 描边
- **完成**：松手后自动保存 + 复制到剪贴板 + 托盘气泡通知

### 自动保存

- 路径：`%USERPROFILE%\Desktop\` （即"桌面"）
- 文件名：`screenshot_YYYYMMDD_HHMMSS.png`（例：`screenshot_20260612_153022.png`）
- 同秒连按自动加 `_2`、`_3` 后缀（不覆盖）
- 格式：PNG（无损，约 50–500 KB / 张，取决于内容复杂度）

### 剪贴板

- 截图**同时**写入 Windows 剪贴板
- 可以直接 `Ctrl+V` 粘贴到：微信、QQ、Word、PowerPoint、Photoshop、浏览器……
- 剪贴板历史（Win+V）也会保留

### 系统托盘

- 启动后**常驻**托盘
- 右键菜单：
  - **退出**：关闭整个程序
- 双击图标 = 触发截图（备用触发方式）

### 通知气泡

- 每次截图后托盘**气泡通知** 3 秒
- 文案：`截图已保存 / 桌面\screenshot_xxx.png / （已复制到剪贴板）`

---

## 快捷键与鼠标

| 操作 | 触发 |
|------|------|
| 启动截图 | `Ctrl+Alt+A` |
| 选区 | 鼠标**左键**按下并拖动 |
| 松开完成 | 鼠标**左键**松开 |
| 取消（选区中） | 按 `Esc` 键 |
| 取消（选区中） | 鼠标**右键** |
| 关闭遮罩 | 托盘 → 退出 |

---

## 截图文件管理

### 批量整理

截图都堆在桌面？两种思路：

**A. 按时间排序**（推荐）：文件名前缀 `screenshot_` 字典序 = 时间序。直接按文件名排序就行。

**B. 定期归档**：每周/每月把 `screenshot_*.png` 移到归档目录。
```bash
# PowerShell — 把所有截图移到 D:\Screenshots\2026-06\
Move-Item $env:USERPROFILE\Desktop\screenshot_*.png D:\Screenshots\2026-06\
```

### 命名冲突

同秒内连按两次 → 自动加 `_2`/`_3` 后缀。不会覆盖。

### 想换文件名 / 路径

当前 MVP 不支持配置（**故意不做**——见设计文档 § 8 范围外）。改源码 `save_to_desktop()` 即可：

```python
# screenshot_tool.py line 11
def save_to_desktop(image: Image.Image) -> Path:
    desktop = Path.home() / "Desktop"
    # ↑ 改这里：换目录
    name = f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
    # ↑ 改这里：换格式（例：加 prefix "myapp_"）
    ...
```

---

## 自定义与进阶

### 改快捷键

编辑 `screenshot_tool.py` 找到这行：
```python
keyboard.add_hotkey("ctrl+alt+a", lambda: self._hotkey_pressed.emit())
```
把 `"ctrl+alt+a"` 换成其他组合（见 [keyboard 库文档](https://github.com/boppreh/keyboard#hotkeys)）：

```python
keyboard.add_hotkey("ctrl+shift+s", ...)  # Chrome 风格
keyboard.add_hotkey("f12", ...)           # 单键
keyboard.add_hotkey("ctrl+alt+shift+a", ...)  # 三键
```

### 加更多快捷键

```python
keyboard.add_hotkey("ctrl+alt+a", lambda: self._hotkey_pressed.emit())
keyboard.add_hotkey("print screen", lambda: self._hotkey_pressed.emit())  # 系统键
```

⚠️ 占用系统键（如 `Print Screen`）会**禁用** Windows 自带的截图行为。

### 改图标

替换 `screenshot_tool.exe` 同目录下的图标文件，或重新 build PyInstaller：
```bash
pyinstaller screenshot_tool.spec --icon=icon.ico
```

### 显示宽高提示

参考设计文档：方案 B / C。需要在 `paintEvent` 加 QPainter 画宽×高文字。

---

## 常见问题

**Q: 启动后没看到托盘图标？**
A:
1. 检查右下角托盘有没有**被折叠**（点 ^ 展开）
2. 右键任务栏 → 设置 → 通知区域 → 找"截图小工具" → 设"显示"
3. 重启程序

**Q: 按 `Ctrl+Alt+A` 没反应？**
A:
1. **快捷键被占**——检查 QQ / 微信 / 网易云 / VSCode 等的全局热键
2. 改 `screenshot_tool.py` 的快捷键（见上）
3. 重启程序

**Q: 截到的是黑屏？**
A: 部分游戏 / 视频播放器用 GPU overlay 渲染，mss 截不到。**不是 bug**——mss 用 GDI 截屏，绕过 GPU。

**Q: 截图区域偏移 / 不准？**
A: 多 DPI 缩放下（125% / 150% / 200%）已处理。如果还有偏差：
1. 检查 Windows 显示设置 → 缩放比例
2. 报 issue 带屏幕缩放比例

**Q: 提示"系统托盘不可用"？**
A: Windows Server / 某些定制系统禁用托盘。**该工具依赖托盘**——无托盘就用不了。

**Q: 能截 GIF / 录视频吗？**
A: 不能。本工具只做**静态截图**。录屏是另一个工具的事。

**Q: exe 怎么这么大（54 MB）？**
A: PyQt5 自带 ~50 MB（Qt 框架）。如需更小：
- 用 PySide6（一样大）
- 改用 Tkinter（自带的，但功能差）

**Q: Linux / macOS 能用吗？**
A: 不能。`mss` 和 `keyboard` 在那两个平台行为不同，PyInstaller 也只打了 Windows build。

**Q: 商业用途可以吗？**
A: MIT License——免费、可商用、改源码都行，保留版权声明即可。

---

## 使用技巧

### 截图 → 微信发图

1. `Ctrl+Alt+A` 选区
2. 切到微信对话框
3. `Ctrl+V` 粘贴 → 发送

不用先保存文件再拖拽。

### 截图 → Markdown 文档

1. 截图
2. 切到 VSCode / Typora
3. `Ctrl+V` → 自动作为 base64 inline 图（或存到 assets 目录）

### 截图 → Excel 表格注释

1. 截图
2. Excel 选单元格 → 右键 → 插入批注
3. 批注框内 `Ctrl+V` → 截图贴在批注里

### 连续截多张

按住 `Ctrl+Alt+A` 不放？不支持。可以**快速**重复按（同秒自动加 `_2` 后缀）。

### 截整个窗口

当前只支持区域选择。截窗口请用 Windows 自带 `Win+Shift+S` 选"窗口"。

### 录屏

本工具不做。Windows 用 `Win+G`（Xbox Game Bar）或 `OBS`。

---

## 卸载

### 如果是 .exe 直拷版
直接删 `screenshot_tool.exe` 和 `_internal/` 文件夹。

### 如果是安装版（Inno Setup 打的）
- 控制面板 → 程序和功能 → 找"截图小工具 v0.1.0" → 卸载
- 或：开始菜单 → 截图小工具 → 卸载

### 清理快捷方式
- 桌面"截图小工具"：右键 → 删除
- 开始菜单磁贴：右键 → 从"开始"菜单取消固定

### 清理截图文件
桌面所有 `screenshot_*.png` 都是工具生成的，可以一起删。

---

## 反馈与支持

- **Bug 报告**：[GitHub Issues](https://github.com/Boris-cpu666/screenshot_tool/issues/new?template=bug_report.md)
- **功能建议**：[GitHub Issues](https://github.com/Boris-cpu666/screenshot_tool/issues/new?template=feature_request.md)
- **README**：[README.md](../README.md)
- **设计文档**：[docs/superpowers/specs/](../superpowers/specs/)
