@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-diagnostics.exe" goto missing
set "ALLPLAN_HOST_URL=http://127.0.0.1:5679"
set "MCP_URL=http://127.0.0.1:8888/mcp"
echo Read-only M1 follow-up: raw identities and parent types in drawing file 101.
.venv\Scripts\allplan-mcp-diagnostics.exe --query-request "docs\probes\m1-component-types.json"
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Extract this probe into the existing installed 0.5.2 evaluation folder.
echo Keep Launch Allplan MCP.cmd open and start StartPythonHost.
pause
exit /b 1
