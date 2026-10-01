; Flux Windows installer
#define MyAppName "Flux"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Flux"
#define MyAppExeName "Flux.exe"

[Setup]
AppId={{A9BEE687-0FB0-467A-9595-62145116D2C1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Flux
DefaultGroupName=Flux
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=release
OutputBaseFilename=FluxSetup
SetupIconFile=assets\flux.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked

[Files]
Source: "dist\Flux\*"; DestDir: "{app}"; Excludes: "database\flux.db"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Flux\database\flux.db"; DestDir: "{app}\database"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\Flux"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\Flux"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Flux"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent
