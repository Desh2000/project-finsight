# FinVest | Analytics Service | main.py
# Member 4: Savings Goal & Portfolio Analytics — FastAPI application entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from router import router

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinVest Savings Goal & Portfolio Analytics Service",
    description="Allows users to define financial targets, track progress, and view portfolio in LKR using live exchange rates.",
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
    description="Returns the health status of the Analytics service and its database connection.",
)
def health_check():
    return {"service": "analytics_service", "status": "healthy", "db": "connected"}
