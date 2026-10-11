@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-selected-mark.exe" goto missing
echo Read-only repair journal inspection. No model read, write, recovery or pruning.
.venv\Scripts\allplan-mcp-selected-mark.exe journal
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
