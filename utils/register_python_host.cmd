@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%..\.venv\Scripts\python.exe" (
    "%SCRIPT_DIR%..\.venv\Scripts\python.exe" "%SCRIPT_DIR%register_python_host.py" %*
) else (
    python "%SCRIPT_DIR%register_python_host.py" %*
)
if errorlevel 1 (
    echo Registration failed.
    exit /b %errorlevel%
)
echo Registration completed. See registration_result.json.
