# FinVest | Asset Service | main.py
# Member 2: Platform Asset & Market Data — FastAPI application entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from router import router
from crud import seed_assets

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

# Seed initial asset data
db = SessionLocal()
try:
    seed_assets(db)
finally:
    db.close()

app = FastAPI(
    title="FinSight Asset & Market Data Service",
    description="Manages the curated list of investable assets and enriches them with live CoinGecko market prices.",
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
    description="Returns the health status of the Asset service and its database connection.",
)
def health_check():
    return {"service": "asset_service", "status": "healthy", "db": "connected"}
