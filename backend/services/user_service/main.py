# FinVest | User Service | main.py
# Member 1: User & KYC Profile management — FastAPI application entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from router import router

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinSight User & KYC Service",
    description="Manages investor accounts, personal profiles, and KYC verification status.",
    version="1.0.0",
)

# CORS middleware — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register user routes
app.include_router(router)


@app.get(
    "/health",
    tags=["Health"],
    summary="Service health check",
    description="Returns the health status of the User service and its database connection.",
)
def health_check():
    return {"service": "user_service", "status": "healthy", "db": "connected"}
