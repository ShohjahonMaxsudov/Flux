@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title Flux Windows Builder

echo.
echo ============================================
echo          FLUX WINDOWS BUILDER
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on PATH.
    echo Install Python 3.10+ and enable "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
python -m pip install --upgrade pip
if errorlevel 1 goto :fail
python -m pip install -r requirements.txt
if errorlevel 1 goto :fail
python -m pip install pyinstaller
if errorlevel 1 goto :fail

echo [2/4] Cleaning old output...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "release" rmdir /s /q "release"

echo [3/4] Building Flux...
python -m PyInstaller Flux.spec --noconfirm --clean
if errorlevel 1 goto :fail

if not exist "dist\Flux\Flux.exe" (
    echo ERROR: dist\Flux\Flux.exe was not created.
    goto :fail
)

echo [4/4] Checking for Inno Setup...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    echo.
    echo Portable build complete:
    echo   dist\Flux\Flux.exe
    echo.
    echo Install Inno Setup 6 and run this file again to also create:
    echo   release\FluxSetup.exe
    echo.
    pause
    exit /b 0
)

"%ISCC%" "installer.iss"
if errorlevel 1 goto :fail

echo.
echo ============================================
echo BUILD COMPLETE
echo ============================================
echo App:       dist\Flux\Flux.exe
echo Installer: release\FluxSetup.exe
echo.
pause
exit /b 0

:fail
echo.
echo BUILD FAILED. Check the error above.
pause
exit /b 1
