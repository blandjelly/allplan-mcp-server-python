@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-recovery-test.exe" goto missing
echo Tylko nowy test na zachowanej kopii. Zapis C03; potem restart hosta i Inspect.
.venv\Scripts\allplan-mcp-recovery-test.exe check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
