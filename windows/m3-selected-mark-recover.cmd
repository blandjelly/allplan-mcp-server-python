@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-selected-mark.exe" goto missing
echo Tylko odczyt zapisanej operacji C04. Bez nowego Apply i wznowienia.
.venv\Scripts\allplan-mcp-selected-mark.exe recover
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
