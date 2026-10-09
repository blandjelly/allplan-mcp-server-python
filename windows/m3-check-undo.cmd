@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-repairs.exe" goto missing
set "ALLPLAN_HOST_URL=http://127.0.0.1:5679"
set "MCP_URL=http://127.0.0.1:8888/mcp"
echo Read-only check after native UI Undo. This command does not invoke Undo.
.venv\Scripts\allplan-mcp-repairs.exe check-undo
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
