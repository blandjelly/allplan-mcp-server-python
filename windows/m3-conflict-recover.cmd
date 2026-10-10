@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-conflicts.exe" goto missing
echo Read-only recovery of the saved C03 conflict-gate execution.
.venv\Scripts\allplan-mcp-conflicts.exe recover
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
