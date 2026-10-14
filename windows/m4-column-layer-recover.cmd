@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\python.exe" goto missing
.venv\Scripts\python.exe -m allplan_mcp.column_layer_diagnostics recover
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
