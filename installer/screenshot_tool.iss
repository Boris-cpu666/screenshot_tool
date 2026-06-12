; Inno Setup Script for screenshot-tool v0.1.0
;
; Prerequisites:
;   1. PyInstaller build artifacts at: dist\screenshot_tool\
;      (run:  pyinstaller screenshot_tool.spec)
;   2. Application icon at: icon.ico
;   3. Inno Setup 6+ installed (download: https://jrsoftware.org/isinfo.php)
;
; Build:
;   Double-click this file in Inno Setup Compiler, OR:
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\screenshot_tool.iss
;
; Output:
;   installer_output\screenshot_tool-v0.1.0-setup.exe   (~50 MB)

#define MyAppName "截图小工具"
#define MyAppNameEn "Screenshot Tool"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Boris-cpu666"
#define MyAppURL "https://github.com/Boris-cpu666/screenshot_tool"
#define MyAppExeName "screenshot_tool.exe"

[Setup]
; NOTE: AppId is a unique GUID identifying this application.
; Do NOT use the same AppId for different applications.
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppNameEn={#MyAppNameEn}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppNameEn}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\README.md
OutputDir=..\installer_output
OutputBaseFilename=screenshot_tool-v{#MyAppVersion}-setup
SetupIconFile=..\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} installer
VersionInfoCopyright=Copyright (c) 2026 {#MyAppPublisher}
MinVersion=10.0

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"
; 中文语言包（Inno Setup 6+ 内置）—— 用 Default.isl 兜底，避免路径问题

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: checkedonce
Name: "startmenu"; Description: "创建开始菜单快捷方式"; GroupDescription: "附加任务:"; Flags: checkedonce

[Files]
; 主程序 + 全部依赖（PyInstaller onedir 输出）
Source: "..\dist\screenshot_tool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; README + LICENSE 也拷过去，方便用户在安装目录看
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 开始菜单
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenu
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenu
Name: "{group}\用户手册 {#MyAppName}"; Filename: "{app}\README.md"; Tasks: startmenu
; 桌面
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent runascurrentuser

[UninstallDelete]
; 卸载时清理整个安装目录
Type: filesanddirs; Name: "{app}"

[Code]
// 安装完成时显示一条提示（不是必须的）
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 不弹窗——已经在 [Run] 段提供"启动"选项
  end;
end;
