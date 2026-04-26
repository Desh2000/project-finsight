#!/bin/bash
# FinVest | start_all.sh
# Starts all microservices, the gateway, and the frontend dev server

echo "======================================"
echo "  Starting FinVest Microservices...   "
echo "======================================"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Start User Service (port 8001)
echo "[1/6] Starting User Service on port 8001..."
cd "$PROJECT_ROOT/services/user_service" && uvicorn main:app --host 0.0.0.0 --port 8001 &

# Start Asset Service (port 8002)
echo "[2/6] Starting Asset Service on port 8002..."
cd "$PROJECT_ROOT/services/asset_service" && uvicorn main:app --host 0.0.0.0 --port 8002 &

# Start Transaction Service (port 8003)
echo "[3/6] Starting Transaction Service on port 8003..."
cd "$PROJECT_ROOT/services/transaction_service" && uvicorn main:app --host 0.0.0.0 --port 8003 &

# Start Analytics Service (port 8004)
echo "[4/6] Starting Analytics Service on port 8004..."
cd "$PROJECT_ROOT/services/analytics_service" && uvicorn main:app --host 0.0.0.0 --port 8004 &

# Start API Gateway (port 8000)
echo "[5/6] Starting API Gateway on port 8000..."
cd "$PROJECT_ROOT/gateway" && uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start Frontend (port 5173)
echo "[6/6] Starting Frontend dev server on port 5173..."
cd "$PROJECT_ROOT/frontend" && npm run dev &

echo ""
echo "======================================"
echo "  All services started!               "
echo "  Gateway:  http://localhost:8000      "
echo "  Frontend: http://localhost:5173      "
echo "  Swagger:  http://localhost:8000/docs "
echo "======================================"

wait
