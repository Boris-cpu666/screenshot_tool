@echo off
REM ============================================================
REM  build_installer.bat — 一键 build Windows 安装程序
REM
REM  Prerequisites:
REM    1. PyInstaller 已装 (pip install pyinstaller)
REM    2. Inno Setup 6+ 已装 (https://jrsoftware.org/isinfo.php)
REM
REM  Usage:
REM    双击运行，或在 cmd 里跑:
REM      build_installer.bat
REM
REM  Output:
REM    installer_output\screenshot_tool-v0.1.0-setup.exe
REM ============================================================

setlocal

echo.
echo ============================================
echo   Screenshot Tool — Build Installer
echo ============================================
echo.

REM ---------- 1. 验证环境 ----------
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller not found.
    echo         Run: pip install pyinstaller
    exit /b 1
)

REM 找 ISCC.exe（Inno Setup 编译器）
set "ISCC="
for %%P in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) do (
    if exist %%~P (
        set "ISCC=%%~P"
        goto :found_iscc
    )
)

:found_iscc
if "%ISCC%"=="" (
    echo [ERROR] Inno Setup 6 not found.
    echo         Download: https://jrsoftware.org/isinfo.php
    exit /b 1
)

echo [OK] PyInstaller:    pyinstaller
echo [OK] Inno Setup:     %ISCC%
echo.

REM ---------- 2. Clean previous build ----------
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist
if exist installer_output rmdir /s /q installer_output
echo [CLEAN] build/ dist/ installer_output/
echo.

REM ---------- 3. PyInstaller build ----------
echo [1/2] Building with PyInstaller...
pyinstaller screenshot_tool.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)
echo.

REM ---------- 4. Inno Setup compile ----------
echo [2/2] Compiling installer with Inno Setup...
"%ISCC%" installer\screenshot_tool.iss
if errorlevel 1 (
    echo [ERROR] Inno Setup compile failed.
    exit /b 1
)
echo.

REM ---------- 5. Done ----------
echo ============================================
echo   DONE
echo ============================================
echo.
echo Output: installer_output\screenshot_tool-v0.1.0-setup.exe
echo.
dir installer_output\*.exe
echo.

endlocal
