@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\python.exe" goto missing
echo M4 0.17.0: slupy bez odpornosci ogniowej - podswietlenie - W1, rysunek 101.
.venv\Scripts\python.exe -m allplan_mcp.column_layer_diagnostics check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
