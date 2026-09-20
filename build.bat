@echo off
setlocal

echo ================================
echo   Flux - local Windows build
echo ================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python was not found on PATH.
    echo     Install Python 3.10+ from https://python.org
    echo     and make sure "Add python.exe to PATH" is checked during setup.
    echo.
    pause
    exit /b 1
)

echo Installing/updating dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo Building Flux.exe with PyInstaller...
python -m PyInstaller Flux.spec --noconfirm

if errorlevel 1 (
    echo.
    echo [!] Build failed - check the messages above.
    pause
    exit /b 1
)

echo.
echo ================================
echo   Build complete
echo ================================
echo Your app:  dist\Flux\Flux.exe
echo (Everything inside dist\Flux needs to stay together - that
echo  whole folder IS the app. Zip it up to share it as-is, or run
echo  ISCC installer.iss, if you have Inno Setup installed, to get
echo  a single FluxSetup.exe installer instead.)
echo.
pause
