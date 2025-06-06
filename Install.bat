@echo off
echo Audio Format Converter Installer
echo ==============================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\AudioFormatConverter"
set "DESKTOP=%USERPROFILE%\Desktop"

echo Installing to: %INSTALL_DIR%
echo.

:: Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\bin" mkdir "%INSTALL_DIR%\bin"
if not exist "%INSTALL_DIR%\dist" mkdir "%INSTALL_DIR%\dist"

:: Copy files
echo Copying application files...
xcopy /Y /E "%~dp0dist\*.*" "%INSTALL_DIR%\dist\"
xcopy /Y /E "%~dp0bin\*.*" "%INSTALL_DIR%\bin\"
copy /Y "%~dp0Setup_and_Run.bat" "%INSTALL_DIR%\"
copy /Y "%~dp0README.md" "%INSTALL_DIR%\"

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Audio Format Converter.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\dist\AudioFormatConverter.exe'; $Shortcut.Description = 'Convert between audio formats without spawning command windows'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%\dist'; $Shortcut.Save()}"

:: Create Start Menu shortcut
echo Creating Start Menu shortcut...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Audio Format Converter"
if not exist "%START_MENU%" mkdir "%START_MENU%"
powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Audio Format Converter.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\dist\AudioFormatConverter.exe'; $Shortcut.Description = 'Convert between audio formats without spawning command windows'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%\dist'; $Shortcut.Save()}"
powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Uninstall Audio Format Converter.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\Uninstall.bat'; $Shortcut.Description = 'Uninstall Audio Format Converter'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()}"

:: Create uninstaller
echo Creating uninstaller...
echo @echo off > "%INSTALL_DIR%\Uninstall.bat"
echo echo Uninstalling Audio Format Converter... >> "%INSTALL_DIR%\Uninstall.bat"
echo del "%DESKTOP%\Audio Format Converter.lnk" >> "%INSTALL_DIR%\Uninstall.bat"
echo rmdir /S /Q "%START_MENU%" >> "%INSTALL_DIR%\Uninstall.bat"
echo cd /d %TEMP% >> "%INSTALL_DIR%\Uninstall.bat"
echo rmdir /S /Q "%INSTALL_DIR%" >> "%INSTALL_DIR%\Uninstall.bat"
echo echo Uninstallation complete. >> "%INSTALL_DIR%\Uninstall.bat"
echo pause >> "%INSTALL_DIR%\Uninstall.bat"

echo.
echo Installation complete!
echo.
echo You can now start Audio Format Converter from:
echo - Desktop shortcut
echo - Start Menu
echo.

pause
