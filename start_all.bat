@echo off
REM FinVest | start_all.bat
REM Starts all microservices, the gateway, and the frontend dev server on Windows

echo ======================================
echo   Starting FinVest Microservices...
echo ======================================

REM Get the project root directory
set PROJECT_ROOT=%~dp0

REM Start User Service (port 8001)
echo [1/6] Starting User Service on port 8001...
start "FinVest-UserService" cmd /c "cd /d %PROJECT_ROOT%services\user_service && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

REM Start Asset Service (port 8002)
echo [2/6] Starting Asset Service on port 8002...
start "FinVest-AssetService" cmd /c "cd /d %PROJECT_ROOT%services\asset_service && uvicorn main:app --host 0.0.0.0 --port 8002 --reload"

REM Start Transaction Service (port 8003)
echo [3/6] Starting Transaction Service on port 8003...
start "FinVest-TransactionService" cmd /c "cd /d %PROJECT_ROOT%services\transaction_service && uvicorn main:app --host 0.0.0.0 --port 8003 --reload"

REM Start Analytics Service (port 8004)
echo [4/6] Starting Analytics Service on port 8004...
start "FinVest-AnalyticsService" cmd /c "cd /d %PROJECT_ROOT%services\analytics_service && uvicorn main:app --host 0.0.0.0 --port 8004 --reload"

REM Start API Gateway (port 8000)
echo [5/6] Starting API Gateway on port 8000...
start "FinVest-Gateway" cmd /c "cd /d %PROJECT_ROOT%gateway && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Start Frontend (port 5173)
echo [6/6] Starting Frontend dev server on port 5173...
start "FinVest-Frontend" cmd /c "cd /d %PROJECT_ROOT%frontend && npm run dev"

echo.
echo ======================================
echo   All services started!
echo   Gateway:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   Swagger:  http://localhost:8000/docs
echo ======================================
echo.
echo Press any key to exit (services will keep running)...
pause >nul
