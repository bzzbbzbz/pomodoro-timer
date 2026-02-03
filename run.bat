@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0src
python -m pomodoro %*
REM Без окна CMD: запустите run.vbs или замените python на pythonw
