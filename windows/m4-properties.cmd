@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\python.exe" goto missing
echo M4 0.16.1: tylko surowe atrybuty jednego slupa w rysunku 101. Bez metadanych, enumow i podswietlenia.
.venv\Scripts\python.exe -m allplan_mcp.property_diagnostics check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
