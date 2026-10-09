@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-repairs.exe" goto missing
set "ALLPLAN_HOST_URL=http://127.0.0.1:5679"
set "MCP_URL=http://127.0.0.1:8888/mcp"
echo M3 write evaluation. Open only the disposable project copy. Read docs\m3-apply-batch.md first.
.venv\Scripts\allplan-mcp-repairs.exe apply
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
