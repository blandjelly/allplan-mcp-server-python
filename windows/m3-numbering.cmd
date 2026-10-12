@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-marks.exe" goto missing
echo New mark-numbering gate on a reviewed disposable project copy.
.venv\Scripts\allplan-mcp-marks.exe --numbering-apply
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
