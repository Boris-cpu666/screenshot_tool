# Screenshot Tool

[![CI](https://github.com/huang/screenshot_tool/actions/workflows/ci.yml/badge.svg)](https://github.com/huang/screenshot_tool/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

轻量 Windows 区域截图小工具。`Ctrl+Alt+A` 拖框截图，自动保存到桌面 + 复制到剪贴板。

Lightweight Windows region-screenshot tool. `Ctrl+Alt+A` to drag-select a region — auto-saves to desktop + copies to clipboard.

## ✨ 特性 / Features

- 🎯 **全局热键** `Ctrl+Alt+A` 触发
- 🖱️ **鼠标拖框**选区域（`Esc` 或右键取消）
- 💾 **自动保存**到桌面，文件名 `screenshot_YYYYMMDD_HHMMSS.png`
- 📋 **自动复制**到剪贴板
- 🖼️ **系统托盘常驻**（右键 → 退出）
- 🖥️ **多显示器**支持
- 🔍 **DPI 缩放**正确处理

## 📦 安装 / Installation

```bash
pip install -r requirements.txt
```

需要 Python 3.10+ 和 Windows 10/11。

## 🚀 运行 / Usage

```bash
python screenshot_tool.py
```

托盘出现后，按 `Ctrl+Alt+A` 拖框截图。

**退出**：托盘图标 → 右键 → 退出。

## 🧪 测试 / Testing

```bash
pip install -r requirements-dev.txt
pytest -v
```

9 个测试覆盖纯函数 + 集成流程（截图 → 保存 → 剪贴板 → 通知）。

## 📦 打包 / Building

生成独立的可执行文件夹（双击即用）：

```bash
pip install pyinstaller
pyinstaller screenshot_tool.spec
```

输出：`dist/screenshot_tool/screenshot_tool.exe`（同目录有 `_internal/` 依赖）。

## 🏗️ 项目结构 / Project Structure

```
screenshot_tool/
├── .github/workflows/ci.yml   # GitHub Actions CI
├── docs/                      # 设计文档
│   └── superpowers/
│       ├── specs/             # 设计规格
│       └── plans/             # 实施计划
├── .gitignore
├── LICENSE                    # MIT
├── README.md                  # 本文件
├── pyproject.toml             # Python 元数据
├── requirements.txt           # 运行时依赖
├── requirements-dev.txt       # 开发/测试依赖
├── pytest.ini
├── screenshot_tool.py         # 主程序（~250 行）
├── screenshot_tool.spec       # PyInstaller 配置
├── test_screenshot_tool.py    # 测试（9 个）
└── manual_check.py            # 视觉调试脚本
```

## 🤝 贡献 / Contributing

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/my-feature`)
3. 提交改动 (`git commit -am 'Add my feature'`)
4. 推送到分支 (`git push origin feature/my-feature`)
5. 创建 Pull Request

**本地开发流程**：
```bash
pip install -r requirements-dev.txt
# 跑测试
pytest -v
# 跑视觉调试
python manual_check.py
```

## 📝 设计文档 / Design Docs

- [设计规格](docs/superpowers/specs/2026-06-12-screenshot-tool-design.md)
- [实施计划](docs/superpowers/plans/2026-06-12-screenshot-tool.md)

## 📄 License

MIT — see [LICENSE](LICENSE).
