!define APP_NAME "Loteria Federal Analytica"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Loteria Caixa Project"
!define APP_DIR "Loteria Federal Analytica"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "LoteriaFederalAnalytica_Installer.exe"
InstallDir "$PROGRAMFILES64\${APP_DIR}"
RequestExecutionLevel admin
Unicode true
SetCompressor /SOLID lzma

Icon "assets\trevo.ico"

Section "Instalar"
  SetOutPath "$INSTDIR"
  File /r "loteria-federal-analytica\*.*"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\cli\app.py" "" "$INSTDIR\assets\trevo.ico"
  CreateShortCut "$STARTMENU\Programs\${APP_NAME}.lnk" "$INSTDIR\cli\app.py" "" "$INSTDIR\assets\trevo.ico"
SectionEnd

Section "Desinstalar"
  RMDir /r "$INSTDIR"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$STARTMENU\Programs\${APP_NAME}.lnk"
SectionEnd
