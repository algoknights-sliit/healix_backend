@echo off
setlocal

REM Change to the project root directory (one level up from /test)
cd /d "%~dp0.."

REM Define Python path (pointing to venv)
set VENV_PATH=venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

echo [1/4] Preparing environment...

REM Ensure no server is already running on 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a > nul 2>&1

if not exist "%PYTHON_EXE%" (
    echo [!] Virtual environment not found. Please run run_tests.bat first.
    exit /b 1
)

echo [2/4] Starting FastAPI server in background...
start /B "" "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > server_log.txt 2>&1

REM Wait for server to initialize
echo [~] Waiting for server to initialize...
ping 127.0.0.1 -n 6 > nul

echo [3/4] Running Integrity Verification (test/verify_integrity.py)...
"%PYTHON_EXE%" test/verify_integrity.py

echo [4/4] Cleaning up server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a > nul 2>&1

echo.
echo Integrity check completed successfully.
pause
