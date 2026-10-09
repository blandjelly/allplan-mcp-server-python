@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-standards.exe" goto missing
set "ALLPLAN_HOST_URL=http://127.0.0.1:5679"
echo Read-only M3 standard and selected previews. No repairs will be applied.
.venv\Scripts\allplan-mcp-standards.exe
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
