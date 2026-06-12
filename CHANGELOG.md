# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Optional region dimensions overlay (方案 B)
- Multiple hotkey modes (fullscreen / region / window)
- Screenshot history panel
- Screenshot annotation (rect / arrow / mosaic / text)

## [0.1.1] - 2026-06-12

### Fixed
- **`requirements.txt` 漏写 `Pillow` 依赖**（`PIL.Image` 在主程序和测试里都用，导致 CI 第一次跑失败）。已补回 runtime + pyproject.toml dependencies。
- **`screenshot_tool.exe` 嵌入应用图标**——之前用 PyInstaller 默认占位，现在 spec 加 `icon='icon.ico'`，exe 实际带紫色相机图标（任务栏 / Alt+Tab / 资源管理器 都生效）。

### Changed
- PyInstaller onedir exe 大小：5.6 MB → 5.8 MB（多 200 KB = 嵌入图标）
- GitHub Release v0.1.1 替代 v0.1.0（54 MB zip）

## [0.1.0] - 2026-06-12

### Added
- Global hotkey `Ctrl+Alt+A` to trigger region screenshot
- Fullscreen translucent overlay with mouse drag selection
- `Esc` or right-click cancels selection
- Auto-save to `~/Desktop/screenshot_YYYYMMDD_HHMMSS.png`
- Filename collision handling (`_2`, `_3` suffixes)
- Auto-copy screenshot to Windows clipboard (RGBA8888 via QClipboard)
- System tray icon with right-click quit menu
- Tray notification bubble on save (3 second timeout)
- Multi-monitor support (`mss.monitors`)
- DPI scaling handling (`QScreen.devicePixelRatio()`)
- Alt+F4 on overlay safely cancels (no crash)
- 9 unit + integration tests (pytest + pytest-qt + freezegun)
- CI: GitHub Actions on Windows × Python 3.10/3.11/3.12/3.13
- PyInstaller onedir build (5.8 MB exe + `_internal/`)
- Application icon (256x256 PNG + multi-size ICO 16/32/48/64/128/256)
- User Guide (中文) at `docs/USER_GUIDE.md`
- Inno Setup installer script at `installer/screenshot_tool.iss`
- Branch protection on `master` (CI required, no force-push)
- GitHub Issue templates (bug report, feature request)
- GitHub Release v0.1.0 with 54 MB Windows zip

### Technical Details
- Python 3.10+ (developed on 3.13)
- Dependencies: PyQt5 ≥5.15, mss ≥9.0, keyboard ≥0.13, **Pillow ≥9.0**
- TDD workflow: red-green-refactor for all features
- Pure functions for IO (`save_to_desktop`, `capture_region`, `copy_to_clipboard`)
- `ScreenshotOverlay(QWidget)` for UI overlay
- `ScreenshotTrayApp(QObject)` for orchestration
- Cross-thread signal bridge for keyboard hook → Qt main thread
- 251 lines main code + 252 lines tests
- MIT License
