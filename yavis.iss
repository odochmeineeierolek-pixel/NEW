[Setup]
AppName=Kyto Task
AppVersion=1.0.0
AppPublisher=KytoTask
DefaultDirName={autopf}\KytoTask
DefaultGroupName=KytoTask
OutputDir=Output
OutputBaseFilename=KytoTask-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\assets\yavis.ico
UninstallDisplayIcon={app}\KytoTask.exe
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Symbole:"
Name: "autostart"; Description: "KytoTask mit Windows starten (optional)"; GroupDescription: "Start:"; Flags: unchecked

[Files]
Source: "..\dist\KytoTask\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\KytoTask"; Filename: "{app}\KytoTask.exe"
Name: "{autodesktop}\KytoTask"; Filename: "{app}\KytoTask.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "KytoTask"; ValueData: """{app}\KytoTask.exe"" --minimized"; Tasks: autostart; Flags: uninsdeletevalue

[Run]
Filename: "{app}\KytoTask.exe"; Description: "KytoTask jetzt starten"; Flags: nowait postinstall skipifsilent
