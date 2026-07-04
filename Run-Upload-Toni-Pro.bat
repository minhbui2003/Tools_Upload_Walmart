@echo off
set TEMP=D:\tmp
set TMP=D:\tmp
if not exist D:\tmp mkdir D:\tmp
echo Starting Upload-Toni-Pro...
start "" "%~dp0dist\POD_Marketplace.exe"
