@echo off
title Stop OpenSuperWhisper
echo Closing OpenSuperWhisper...
wmic process where "commandline like '%%main.py%%'" call terminate >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq OpenSuperWhisper*" >nul 2>&1
echo OpenSuperWhisper process stopped.
ping 127.0.0.1 -n 2 >nul
exit
