@echo off
title OpenSuperWhisper Launcher
echo Starting OpenSuperWhisper for Windows (x64)...
start "OpenSuperWhisper" python "%~dp0main.py"
echo OpenSuperWhisper started successfully!
ping 127.0.0.1 -n 2 >nul
exit
