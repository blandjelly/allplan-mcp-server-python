@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp.exe" goto missing
set "ALLPLAN_MCP_ENABLE_PYTHON_EXEC=0"
set "ALLPLAN_HOST_URL=http://127.0.0.1:5679"
set "MCP_HOST=127.0.0.1"
set "MCP_PORT=8888"
set "MCP_PATH=/mcp"
set "ALLPLAN_MCP_EVIDENCE_DIR=%CD%\logs\evidence"
echo Keep this window open. MCP endpoint: http://127.0.0.1:8888/mcp
echo Raw bridge evidence: %ALLPLAN_MCP_EVIDENCE_DIR%
.venv\Scripts\allplan-mcp.exe
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
