@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\python.exe" goto missing
echo M4: sciany jednowarstwowe ponizej 24 cm, rysunek 101. Odczyt i podswietlenie.
.venv\Scripts\python.exe -m allplan_mcp.wall_filter_diagnostics
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
