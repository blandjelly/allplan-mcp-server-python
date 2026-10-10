@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-workflows.exe" goto missing
echo Read-only recovery of the last numbering execution. No Apply, setter or Undo.
.venv\Scripts\allplan-mcp-workflows.exe recover --execution logs\m3-last-numbering-execution.json
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
