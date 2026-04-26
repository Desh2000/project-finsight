# FinVest | API Gateway | main.py

import time
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import SERVICE_MAP, SERVICE_NAMES
from gateway_routes import router as proxy_router   # ← import here

app = FastAPI(
    title="FinSight API Gateway",
    description=(
        "Unified API Gateway for all FinSight microservices. "
        "Proxies requests to User (8001), Asset (8002), Transaction (8003), and Analytics (8004) services."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = round((time.time() - start) * 1000, 2)
    print(f"[GATEWAY] {request.method} {request.url.path} → {response.status_code} ({latency}ms)")
    return response

@app.get("/health", tags=["Gateway"], summary="Gateway + all services health check")
async def health_check():
    services_status = {}

    async def check_service(name: str, base_url: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{base_url}/health")
                services_status[name] = "healthy" if resp.status_code == 200 else "unreachable"
        except Exception:
            services_status[name] = "unreachable"

    await asyncio.gather(*[
        check_service(SERVICE_NAMES[key], url)
        for key, url in SERVICE_MAP.items()
    ])
    return {"gateway": "healthy", "services": services_status}

app.include_router(proxy_router)  # ← registers all static proxy routes