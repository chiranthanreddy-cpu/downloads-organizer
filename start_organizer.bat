@echo off
title Downloads Organizer - Background Mode
cd /d "%~dp0"
echo Starting Downloads Organizer in background mode...
python organize_downloads.py --watch
pause
