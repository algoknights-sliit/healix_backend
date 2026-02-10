@echo off
setlocal

:: Change to the project root directory (one level up from /test)
cd /d "%~dp0.."

:: Define Python path (pointing to venv)
set VENV_PATH=venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe
set PIP_EXE=%VENV_PATH%\Scripts\pip.exe

:: Check if venv exists, if not create it
if not exist "%PYTHON_EXE%" (
    echo [!] Virtual environment not found at %VENV_PATH%. Creating one...
    python -m venv %VENV_PATH%
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

echo [1/5] Checking environment...
"%PYTHON_EXE%" -c "import fastapi, uvicorn, sqlalchemy, pydantic" >nul 2>&1
if %errorlevel% neq 0 (
    echo Requirements not met. Installing...
    "%PIP_EXE%" install -r requirements.txt
) else (
    echo Requirements already satisfied. Skipping install.
)

echo [2/5] Starting FastAPI server on port 8000...
:: Start the server in the background using venv
start /B "" "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo [3/5] Waiting for server to initialize...
timeout /t 5 /nobreak > nul

echo [4/5] Running verification tests (test/verify_crud.py)...
"%PYTHON_EXE%" test/verify_crud.py

echo [5/5] Cleaning up (Stopping server on port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process PID: %%a
    taskkill /F /PID %%a > nul 2>&1
)

echo.
echo Tests completed.
pause
