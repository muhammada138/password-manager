@echo off
echo [1/5] Removing from Windows Startup...
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "OmniVault" /f 2>nul

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
