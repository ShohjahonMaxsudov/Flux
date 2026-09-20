; Inno Setup script for Flux.
; Build the app first (pyinstaller Flux.spec / build.bat), THEN compile
; this with Inno Setup (https://jrsoftware.org/isinfo.php) to get
; installer_output\FluxSetup.exe — a normal Windows installer with a
; wizard, Start Menu / Desktop shortcuts, and an uninstaller.

#define MyAppName "Flux"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Flux"
#define MyAppExeName "Flux.exe"

[Setup]
AppId={{2F6B9C6E-6E2A-4E3A-9B7D-5A7DFF0F1FA0}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=FluxSetup
Compression=lzma2
SolidCompression=yes
SetupIconFile=assets\icon.ico
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\Flux\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
