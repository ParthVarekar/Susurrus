@echo off
setlocal enabledelayedexpansion
title OpenSuperWhisper Control Panel

:MENU
cls
echo ========================================================
echo               OPEN SUPER WHISPER (Windows x64)
echo ========================================================
echo.
echo [1] Start OpenSuperWhisper
echo [2] Stop OpenSuperWhisper
echo [3] Check Status
echo [4] Exit
echo.
echo ========================================================
set /p CHOICE="Select an option [1-4]: "

if "%CHOICE%"=="1" goto START_APP
if "%CHOICE%"=="2" goto STOP_APP
if "%CHOICE%"=="3" goto CHECK_STATUS
if "%CHOICE%"=="4" exit
goto MENU

:START_APP
echo.
echo Launching OpenSuperWhisper...
start "OpenSuperWhisper" python "%~dp0main.py"
echo Done! App is running.
ping 127.0.0.1 -n 3 >nul
goto MENU

:STOP_APP
echo.
echo Stopping OpenSuperWhisper...
wmic process where "commandline like '%%main.py%%'" call terminate >nul 2>&1
echo Done!
ping 127.0.0.1 -n 3 >nul
goto MENU

:CHECK_STATUS
echo.
echo Checking process status...
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Status: Python processes running (OpenSuperWhisper active).
) else (
    echo Status: OpenSuperWhisper is NOT running.
)
pause
goto MENU
