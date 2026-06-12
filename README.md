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
