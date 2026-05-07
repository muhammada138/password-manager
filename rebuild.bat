@echo off
echo [1/5] Checking and restoring Windows Startup settings...
for /f "delims=" %%a in ('powershell -command "if (Test-Path 'settings.json') { (Get-Content settings.json | ConvertFrom-Json).startup } else { $false }"') do set STARTUP_STATE=%%a
if /I "%STARTUP_STATE%"=="True" (
    echo [INFO] Load with Startup is ON. Re-registering...
    reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "OmniVault" /t REG_SZ /d "\"%~dp0OmniVault.exe\" --startup" /f >nul
) else (
    echo [INFO] Load with Startup is OFF. Ensuring registry key is removed...
    reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "OmniVault" /f 2>nul
)

echo [2/5] Cleaning old build artifacts...
if exist OmniVault.exe del /F /Q OmniVault.exe
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build
if exist OmniVault.spec del /F /Q OmniVault.spec

echo [3/5] Building OmniVault.exe...
pyinstaller --noconfirm --onefile --windowed --icon="vault_icon.ico" --name "OmniVault" secure_switcher.py

echo [4/5] Moving new executable...
move /Y "dist\OmniVault.exe" "."

echo [5/5] Final cleanup...
rmdir /S /Q dist
rmdir /S /Q build
del /F /Q OmniVault.spec

echo Done! OmniVault.exe has been rebuilt and is ready.
pause
