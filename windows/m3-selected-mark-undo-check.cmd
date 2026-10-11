@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-selected-mark.exe" goto missing
echo Kontrola po jednym Undo C04. Bez Apply. Zachowaj te sama kopie projektu.
.venv\Scripts\allplan-mcp-selected-mark.exe undo-check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
