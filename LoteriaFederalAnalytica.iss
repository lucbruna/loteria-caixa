[Setup]
AppName=Loteria Federal Analytica
AppVersion=1.0.0
AppPublisher=Loteria Caixa Project
AppPublisherURL=https://github.com/lucbruna/loteria-caixa
DefaultDirName={pf64}\Loteria Federal Analytica
DefaultGroupName=Loteria Federal Analytica
OutputDir=dist_installer
OutputBaseFilename=LoteriaFederalAnalytica_Installer_Inno
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\trevo.ico
UninstallDisplayIcon={app}\assets\trevo.ico

[Files]
Source: "src\*"; DestDir: "{app}\src"; Flags: recursesubdirs
Source: "cli\*"; DestDir: "{app}\cli"; Flags: recursesubdirs
Source: "data\*"; DestDir: "{app}\data"; Flags: recursesubdirs
Source: "reports\*"; DestDir: "{app}\reports"; Flags: recursesubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: recursesubdirs
Source: "tests\*"; DestDir: "{app}\tests"; Flags: recursesubdirs
Source: "assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs
Source: "auditoria_completa.md"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"
Source: "roadmap_turbinar_ultra_top.md"; DestDir: "{app}"
Source: "requirements.txt"; DestDir: "{app}"
Source: "Makefile"; DestDir: "{app}"
Source: "install.nsi"; DestDir: "{app}"
Source: "LoteriaFederalAnalytica.iss"; DestDir: "{app}"

[Icons]
Name: "{group}\Loteria Federal Analytica"; Filename: "{app}\cli\app.py"; IconFilename: "{app}\assets\trevo.ico"
Name: "{commondesktop}\Loteria Federal Analytica"; Filename: "{app}\cli\app.py"; IconFilename: "{app}\assets\trevo.ico"

[Run]
Filename: "{app}\README.md"; Description: "Ver README"; Flags: postinstall shellexec
