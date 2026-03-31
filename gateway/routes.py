# FinVest | API Gateway | routes.py
# Gateway: Proxy route definitions mapping frontend requests to microservices

# ── Service port mapping ──
SERVICE_MAP = {
    "users": "http://localhost:8001",
    "assets": "http://localhost:8002",
    "transactions": "http://localhost:8003",
    "analytics": "http://localhost:8004",
}

# Service names for display
SERVICE_NAMES = {
    "users": "user_service",
    "assets": "asset_service",
    "transactions": "transaction_service",
    "analytics": "analytics_service",
}

SERVICE_PATH_MAP = {
    "users": "api/users",
    "assets": "api/assets",
    "transactions": "api/transactions",
    "analytics": "api/analytics",
}