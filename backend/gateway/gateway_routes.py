# FinSight | API Gateway | gateway_routes.py
# Static proxy route definitions for all downstream microservices

import httpx
from fastapi import APIRouter, Request, Response
from routes import SERVICE_MAP
from schemas import (
    UserCreate, UserUpdate, KYCUpdate, AssetCreate, AssetUpdate, TradeableToggle,
    GoalCreate, GoalUpdate, DepositRequest,
    TransactionCreate, TransactionStatusUpdate,
    TransactionResponse, TransactionListResponse, TransactionSummaryResponse,
)


# ── Base URLs ──
USERS_URL     = SERVICE_MAP["users"]        # http://localhost:8001
ASSETS_URL    = SERVICE_MAP["assets"]       # http://localhost:8002
TXN_URL       = SERVICE_MAP["transactions"] # http://localhost:8003
ANALYTICS_URL = SERVICE_MAP["analytics"]    # http://localhost:8004

router = APIRouter()


# ── Shared proxy helper ──
async def forward(method: str, target_url: str, request: Request) -> Response:
    if request.url.query:
        target_url += f"?{request.url.query}"

    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.request(method=method, url=target_url, content=body, headers=headers)
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type=resp.headers.get("content-type", "application/json"),
            )
    except httpx.TimeoutException:
        return Response(
            content='{"detail": "Gateway timeout: downstream service did not respond within 5 seconds"}',
            status_code=504, media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            content='{"detail": "Service is unreachable"}',
            status_code=502, media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Gateway error: {str(e)}"}}',
            status_code=500, media_type="application/json",
        )


# ══════════════════════════════════════════════════════
#  USER SERVICE  —  /api/users  (port 8001)
# ══════════════════════════════════════════════════════

@router.post("/gateway/users/register", tags=["Users"], summary="Register a new user")
async def register_user(user_data: UserCreate, request: Request):
    return await forward("POST", f"{USERS_URL}/api/users/register", request)

@router.get("/gateway/users/", tags=["Users"], summary="List all active users")
async def list_users(request: Request):
    return await forward("GET", f"{USERS_URL}/api/users/", request)

@router.get("/gateway/users/{user_id}", tags=["Users"], summary="Get user profile")
async def get_user(user_id: str, request: Request):
    return await forward("GET", f"{USERS_URL}/api/users/{user_id}", request)

@router.put("/gateway/users/{user_id}", tags=["Users"], summary="Update user profile")
async def update_user(user_id: str, update_data: UserUpdate, request: Request):
    return await forward("PUT", f"{USERS_URL}/api/users/{user_id}", request)

@router.patch("/gateway/users/{user_id}/kyc", tags=["Users"], summary="Update KYC status")
async def update_kyc(user_id: str, kyc_data: KYCUpdate, request: Request):
    return await forward("PATCH", f"{USERS_URL}/api/users/{user_id}/kyc", request)

@router.delete("/gateway/users/{user_id}/remove", tags=["Users"], summary="Hard-delete a user")
async def hard_delete_user(user_id: str, request: Request):
    return await forward("DELETE", f"{USERS_URL}/api/users/{user_id}/remove", request)

@router.delete("/gateway/users/{user_id}", tags=["Users"], summary="Soft-delete a user")
async def delete_user(user_id: str, request: Request):
    return await forward("DELETE", f"{USERS_URL}/api/users/{user_id}", request)


# ══════════════════════════════════════════════════════
#  ASSET SERVICE  —  /api/assets  (port 8002)
# ══════════════════════════════════════════════════════

@router.post("/gateway/assets/", tags=["Assets"], summary="Add a new asset")
async def create_asset(asset_data: AssetCreate, request: Request):
    return await forward("POST", f"{ASSETS_URL}/api/assets/", request)

@router.get("/gateway/assets/", tags=["Assets"], summary="List all assets with live prices")
async def list_assets(request: Request):
    return await forward("GET", f"{ASSETS_URL}/api/assets/", request)

@router.get("/gateway/assets/ticker/{ticker}", tags=["Assets"], summary="Look up asset by ticker")
async def get_asset_by_ticker(ticker: str, request: Request):
    return await forward("GET", f"{ASSETS_URL}/api/assets/ticker/{ticker}", request)

@router.get("/gateway/assets/{asset_id}", tags=["Assets"], summary="Get asset by ID")
async def get_asset(asset_id: str, request: Request):
    return await forward("GET", f"{ASSETS_URL}/api/assets/{asset_id}", request)

@router.put("/gateway/assets/{asset_id}", tags=["Assets"], summary="Update asset metadata")
async def update_asset(asset_id: str, update_data: AssetUpdate, request: Request):
    return await forward("PUT", f"{ASSETS_URL}/api/assets/{asset_id}", request)

@router.patch("/gateway/assets/{asset_id}/tradeable", tags=["Assets"], summary="Toggle tradeable status")
async def toggle_tradeable(asset_id: str, toggle: TradeableToggle, request: Request):
    return await forward("PATCH", f"{ASSETS_URL}/api/assets/{asset_id}/tradeable", request)

@router.delete("/gateway/assets/{asset_id}", tags=["Assets"], summary="Delete an asset")
async def delete_asset(asset_id: str, request: Request):
    return await forward("DELETE", f"{ASSETS_URL}/api/assets/{asset_id}", request)


# ══════════════════════════════════════════════════════
#  TRANSACTION SERVICE  —  /api/transactions  (port 8003)
# ══════════════════════════════════════════════════════

@router.post("/gateway/transactions/", tags=["Transactions"], summary="Place a new order")
async def create_transaction(txn_data: TransactionCreate, request: Request):
    return await forward("POST", f"{TXN_URL}/api/transactions/", request)

@router.get("/gateway/transactions/", tags=["Transactions"], summary="List all transactions")
async def list_transactions(request: Request):
    return await forward("GET", f"{TXN_URL}/api/transactions/", request)

@router.get("/gateway/transactions/summary/{user_id}", tags=["Transactions"], summary="User transaction summary")
async def get_user_summary(user_id: str, request: Request):
    return await forward("GET", f"{TXN_URL}/api/transactions/summary/{user_id}", request)

@router.get("/gateway/transactions/user/{user_id}", tags=["Transactions"], summary="User transaction history")
async def get_user_transactions(user_id: str, request: Request):
    return await forward("GET", f"{TXN_URL}/api/transactions/user/{user_id}", request)

@router.get("/gateway/transactions/{txn_id}", tags=["Transactions"], summary="Get transaction receipt")
async def get_transaction(txn_id: str, request: Request):
    return await forward("GET", f"{TXN_URL}/api/transactions/{txn_id}", request)

@router.patch("/gateway/transactions/{txn_id}/status", tags=["Transactions"], summary="Update order status")
async def update_transaction_status(txn_id: str, status_data: TransactionStatusUpdate, request: Request):
    return await forward("PATCH", f"{TXN_URL}/api/transactions/{txn_id}/status", request)

@router.delete("/gateway/transactions/{txn_id}/delete", tags=["Transactions"], summary="Permanently delete a transaction")
async def delete_transaction(txn_id: str, request: Request):
    return await forward("DELETE", f"{TXN_URL}/api/transactions/{txn_id}/delete", request)

@router.delete("/gateway/transactions/{txn_id}", tags=["Transactions"], summary="Cancel a pending order")
async def cancel_transaction(txn_id: str, request: Request):
    return await forward("DELETE", f"{TXN_URL}/api/transactions/{txn_id}", request)


# ══════════════════════════════════════════════════════
#  ANALYTICS SERVICE  —  /api/analytics  (port 8004)
# ══════════════════════════════════════════════════════

@router.post("/gateway/analytics/goals/", tags=["Analytics"], summary="Create a savings goal")
async def create_goal(goal_data: GoalCreate, request: Request):
    return await forward("POST", f"{ANALYTICS_URL}/api/analytics/goals/", request)

@router.get("/gateway/analytics/goals/", tags=["Analytics"], summary="List savings goals")
async def list_goals(request: Request):
    return await forward("GET", f"{ANALYTICS_URL}/api/analytics/goals/", request)

# /portfolio/{user_id} before /goals/{goal_id} to avoid collision
@router.get("/gateway/analytics/portfolio/{user_id}", tags=["Analytics"], summary="Portfolio analytics")
async def get_portfolio(user_id: str, request: Request):
    return await forward("GET", f"{ANALYTICS_URL}/api/analytics/portfolio/{user_id}", request)

@router.get("/gateway/analytics/goals/{goal_id}", tags=["Analytics"], summary="Get a savings goal")
async def get_goal(goal_id: str, request: Request):
    return await forward("GET", f"{ANALYTICS_URL}/api/analytics/goals/{goal_id}", request)

@router.get("/gateway/analytics/goals/{goal_id}/predict", tags=["Analytics"], summary="ML risk prediction for a savings goal")
async def get_goal_prediction(goal_id: str, request: Request):
    return await forward("GET", f"{ANALYTICS_URL}/api/analytics/goals/{goal_id}/predict", request)

@router.put("/gateway/analytics/goals/{goal_id}", tags=["Analytics"], summary="Update a savings goal")
async def update_goal(goal_id: str,  update_data: GoalUpdate, request: Request):
    return await forward("PUT", f"{ANALYTICS_URL}/api/analytics/goals/{goal_id}", request)

@router.patch("/gateway/analytics/goals/{goal_id}/deposit", tags=["Analytics"], summary="Deposit into a savings goal")
async def deposit_goal(goal_id: str, deposit_data: DepositRequest, request: Request):
    return await forward("PATCH", f"{ANALYTICS_URL}/api/analytics/goals/{goal_id}/deposit", request)

@router.delete("/gateway/analytics/goals/{goal_id}", tags=["Analytics"], summary="Abandon a savings goal")
async def delete_goal(goal_id: str, request: Request):
    return await forward("DELETE", f"{ANALYTICS_URL}/api/analytics/goals/{goal_id}", request)

@router.delete("/gateway/analytics/goals/{goal_id}/permanent", tags=["Analytics"], summary="Permanently delete a savings goal")
async def delete_goal_permanent(goal_id: str, request: Request):
    return await forward("DELETE", f"{ANALYTICS_URL}/api/analytics/goals/{goal_id}/permanent", request)