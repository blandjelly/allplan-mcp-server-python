@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-conflicts.exe" goto missing
echo Same-session source conflict gate on the original disposable copy.
.venv\Scripts\allplan-mcp-conflicts.exe check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
