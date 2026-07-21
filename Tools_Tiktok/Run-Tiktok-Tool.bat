@echo off
cd /d "%~dp0"
set TEMP=D:\tmp
set TMP=D:\tmp
if not exist D:\tmp mkdir D:\tmp
echo Starting TikTok Upload Tool...
python main.py
