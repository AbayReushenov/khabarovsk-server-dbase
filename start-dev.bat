@echo off
:: 🏔️ Khabarovsk Forecast Buddy - Development Startup Script (Windows)
:: Starts both frontend and backend simultaneously

setlocal EnableDelayedExpansion

:: Configuration
set BACKEND_DIR=%cd%
set FRONTEND_DIR=..\habarovsk-forecast-buddy
set BACKEND_PORT=8000
set FRONTEND_PORT=8080

echo 🏔️  Khabarovsk Forecast Buddy - Development Startup
echo =================================================

:: Check if directories exist
if not exist "%FRONTEND_DIR%" (
    echo ❌ Frontend directory not found: %FRONTEND_DIR%
    echo 💡 Make sure both repositories are in the same parent directory
    pause
    exit /b 1
)

echo 🔍 Checking prerequisites...

:: Check backend dependencies
echo 🔧 Checking backend...
if not exist "requirements.txt" (
    echo ❌ Backend requirements.txt not found
    pause
    exit /b 1
)

if not exist "venv" (
    echo ⚠️  Virtual environment not found, creating...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install/update backend dependencies
echo 📦 Installing backend dependencies...
pip install -r requirements.txt >nul 2>&1

:: Check .env file
if not exist ".env" (
    echo ❌ .env file not found in backend
    echo 💡 Copy .env.example and configure your settings
    pause
    exit /b 1
)

:: Check frontend dependencies
echo 🔧 Checking frontend...
cd "%FRONTEND_DIR%"

if not exist "package.json" (
    echo ❌ Frontend package.json not found
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
) else (
    echo ✅ Frontend dependencies found
)

:: Return to backend directory
cd "%BACKEND_DIR%"

echo ✅ Prerequisites check complete
echo.

:: Start backend
echo 🚀 Starting Backend (FastAPI)...
echo    URL: http://localhost:%BACKEND_PORT%
echo    API Docs: http://localhost:%BACKEND_PORT%/docs

start "Khabarovsk Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port %BACKEND_PORT%"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
echo 🚀 Starting Frontend (React + Vite)...
echo    URL: http://localhost:%FRONTEND_PORT%

cd "%FRONTEND_DIR%"
start "Khabarovsk Frontend" cmd /k "npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT%"

:: Return to backend directory
cd "%BACKEND_DIR%"

echo.
echo 🎉 Development environment is starting!
echo =================================================
echo 📱 Frontend:    http://localhost:%FRONTEND_PORT%
echo ⚙️  Backend:     http://localhost:%BACKEND_PORT%
echo 📚 API Docs:    http://localhost:%BACKEND_PORT%/docs
echo 💾 Health:      http://localhost:%BACKEND_PORT%/api/v1/health
echo =================================================
echo.
echo 📋 Development Tips:
echo    • Both services will open in separate windows
echo    • Frontend auto-reloads on file changes
echo    • Backend auto-reloads on Python file changes
echo    • Close the windows to stop services
echo.

pause
