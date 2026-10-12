@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-recovery-test.exe" goto missing
echo Inspekcja po restarcie StartPythonHost. Bez ponownego Test i bez Undo do wyniku.
.venv\Scripts\allplan-mcp-recovery-test.exe recover
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
