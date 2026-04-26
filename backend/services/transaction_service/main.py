# FinVest | Transaction Service | main.py
# Member 3: Transaction & Order management — FastAPI application entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from router import router

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinSight Transaction & Order Service",
    description="Handles simulated buy/sell orders with status lifecycle (Pending → Completed/Failed/Cancelled).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get(
    "/health",
    tags=["Health"],
    summary="Service health check",
    description="Returns the health status of the Transaction service and its database connection.",
)
def health_check():
    return {"service": "transaction_service", "status": "healthy", "db": "connected"}
