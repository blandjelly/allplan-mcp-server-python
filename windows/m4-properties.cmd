@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\python.exe" goto missing
echo M4: odczyt wlasciwosci i podswietlenie slupow/scian. Bez zapisu modelu.
.venv\Scripts\python.exe -m allplan_mcp.property_diagnostics check
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
