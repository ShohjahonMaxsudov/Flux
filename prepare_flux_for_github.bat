@echo off
setlocal EnableExtensions
title Prepare Flux for GitHub

set "APP="

REM Best way: drag the Flux folder onto this BAT.
if not "%~1"=="" (
    if exist "%~1\main.py" set "APP=%~1"
)

REM Or place this BAT inside the Flux folder.
if not defined APP (
    if exist "%~dp0main.py" set "APP=%~dp0"
)

REM Or place this BAT beside a folder named Flux.
if not defined APP (
    if exist "%~dp0Flux\main.py" set "APP=%~dp0Flux"
)

if not defined APP (
    echo.
    echo Could not find Flux\main.py.
    echo.
    echo EASIEST FIX:
    echo Drag your extracted Flux folder onto this BAT file.
    echo.
    pause
    exit /b 1
)

echo.
echo Flux found:
echo %APP%
echo.

echo Removing generated Python cache files...
for /d /r "%APP%" %%D in (__pycache__) do (
    if exist "%%D" rd /s /q "%%D"
)
del /s /q "%APP%\*.pyc" 2>nul
del /s /q "%APP%\*.pyo" 2>nul

if exist "%APP%\requirements.txt.txt" del /q "%APP%\requirements.txt.txt"
if exist "%APP%\build" rd /s /q "%APP%\build"
if exist "%APP%\dist" rd /s /q "%APP%\dist"
if exist "%APP%\release" rd /s /q "%APP%\release"

echo.
echo Done.
echo Your source code, assets, database and main.py were NOT deleted.
echo.
echo Now add installer.iss, .gitignore and the .github folder from this kit
echo into the Flux folder, then upload/push Flux to GitHub.
echo.
pause
