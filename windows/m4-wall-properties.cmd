@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\python.exe" goto missing
echo M4: odczyt jednej jednowarstwowej sciany w rysunku 101. Bez zapisu i podswietlenia.
.venv\Scripts\python.exe -m allplan_mcp.wall_diagnostics
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
