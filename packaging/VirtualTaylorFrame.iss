#define AppName "Virtual Taylor Frame"
#define AppVersion "0.1.0"
#define AppPublisher "Virtual Taylor Frame"
#define AppExeName "VirtualTaylorFrame.exe"

[Setup]
AppId={{A8F7B9B9-8E22-4D5E-9E3C-7A8F6B9D2E10}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Virtual Taylor Frame
DefaultGroupName={#AppName}
OutputDir=..\dist
OutputBaseFilename=VirtualTaylorFrame-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
Uninstallable=yes
PrivilegesRequired=lowest

[Files]
Source: "..\dist\VirtualTaylorFrame\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Virtual Taylor Frame"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\Virtual Taylor Frame"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch Virtual Taylor Frame"; Flags: nowait postinstall skipifsilent
