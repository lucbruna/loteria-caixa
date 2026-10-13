; Inno Setup script - Loteria Federal IA
; Gera um instalador profissional (setup) para Windows.
;
; Compilar: iscc LoteriaFederal.iss
; Requer Inno Setup (https://jrsoftware.org/isdl.php)

#define MyAppName "Loteria Federal IA"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Loteria Federal IA"
#define MyAppURL "https://www.loteriafederal.gov.br"
#define MyAppExeName "LoteriaFederal.exe"
#define MyAppGUID "8F3E2C1A-5B7D-4E9F-A2C6-1D3E4F5A6B7C"

[Setup]
AppId={#MyAppGUID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName}
VersionInfoCopyright=Copyright (c) 2024
SetupIconFile=Distribuicao\icon.ico
InfoBeforeFile=Distribuicao\LEIA_ANTES.txt
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=Distribuicao\EULA.txt
OutputDir=dist_installer
OutputBaseFilename=LoteriaFederal-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64os
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
LanguageDetectionMethod=uilanguage
ShowLanguageDialog=auto

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "dist\LoteriaFederal.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\LoteriaFederal-Console.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} (Menu)"; Filename: "{app}\LoteriaFederal-Console.exe"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName} ao concluir"; Flags: nowait postinstall runascurrentuser unchecked
