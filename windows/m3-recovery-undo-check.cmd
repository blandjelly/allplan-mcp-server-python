@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-recovery-test.exe" goto missing
echo Koncowy odczyt po jednym Undo. Zachowaj projekt i dziennik.
.venv\Scripts\allplan-mcp-recovery-test.exe undo-check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
