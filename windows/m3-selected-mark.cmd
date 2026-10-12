@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-selected-mark.exe" goto missing
echo Nowy test: tylko C04 S02 - S04, C02 wykluczony. Nie powtarzaj po zapisaniu ID.
.venv\Scripts\allplan-mcp-selected-mark.exe check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
