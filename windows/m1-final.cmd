@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
if not exist ".venv\Scripts\allplan-mcp-diagnostics.exe" goto missing
set "ALLPLAN_HOST_URL=http://127.0.0.1:5679"
set "MCP_URL=http://127.0.0.1:8888/mcp"
echo Read-only M1 final batch: demo resources, files 101-103, geometry and native hierarchy.
echo Start StartPythonHost after setting the drawing-file states. Keep it running.
.venv\Scripts\allplan-mcp-diagnostics.exe --query-batch "docs\probes\m1-final.json"
set "ACTION_RESULT=%ERRORLEVEL%"
pause
exit /b %ACTION_RESULT%
:missing
echo Run Setup.cmd first.
pause
exit /b 1
