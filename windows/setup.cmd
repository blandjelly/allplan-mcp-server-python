@echo off
setlocal
cd /d "%~dp0"
if not exist "pyproject.toml" cd ..
echo Allplan MCP 0.3.0 evaluation setup. Close Allplan before installing.
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))"
if errorlevel 1 goto runtime_error
py -3 -m venv .bootstrap
if errorlevel 1 goto failed
goto bootstrap
:python_fallback
python -c "import sys; sys.exit(sys.version_info < (3, 11))"
if errorlevel 1 goto runtime_error
python -m venv .bootstrap
if errorlevel 1 goto failed
:bootstrap
.bootstrap\Scripts\python.exe windows\actions.py verify
if errorlevel 1 goto failed
.bootstrap\Scripts\python.exe -m pip install uv==0.12.19
if errorlevel 1 goto failed
.bootstrap\Scripts\uv.exe sync --frozen --no-dev --no-editable --python .bootstrap\Scripts\python.exe
if errorlevel 1 goto failed
.venv\Scripts\python.exe windows\actions.py install
if errorlevel 1 goto failed
echo Setup completed. Follow README.md, then Launch Allplan MCP.cmd.
pause
exit /b 0
:runtime_error
echo Install Python 3.11 or newer for Windows from https://www.python.org/downloads/windows/
echo This is the external server runtime. Do not use Allplan's embedded Python.
pause
exit /b 1
:failed
echo Setup failed. The console above contains the error. Do not continue with UAT.
pause
exit /b 1
