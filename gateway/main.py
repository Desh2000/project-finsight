# FinVest | API Gateway | main.py
# Gateway: Single entry point that proxies all requests to downstream microservices

import time
import asyncio
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from routes import SERVICE_MAP, SERVICE_NAMES, SERVICE_PATH_MAP

app = FastAPI(
    title="FinSight API Gateway",
    description=(
        "Unified API Gateway for all FinSight microservices. "
        "Proxies requests to User (8001), Asset (8002), Transaction (8003), and Analytics (8004) services."
    ),
    version="1.0.0",
)

# ── CORS middleware — allow all origins for local development ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware ──
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = round((time.time() - start) * 1000, 2)
    print(f"[GATEWAY] {request.method} {request.url.path} → {response.status_code} ({latency}ms)")
    return response


# ── Health check — calls all 4 services in parallel ──
@app.get(
    "/health",
    tags=["Gateway"],
    summary="Gateway health check",
    description="Checks the health of the gateway and all downstream microservices in parallel.",
)
async def health_check():
    services_status = {}

    async def check_service(name: str, base_url: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{base_url}/health")
                if resp.status_code == 200:
                    services_status[name] = "healthy"
                else:
                    services_status[name] = "unreachable"
        except Exception:
            services_status[name] = "unreachable"

    # Check all services concurrently
    tasks = [
        check_service(SERVICE_NAMES[key], url)
        for key, url in SERVICE_MAP.items()
    ]
    await asyncio.gather(*tasks)

    return {
        "gateway": "healthy",
        "services": services_status,
    }


# - Catch-all proxy route -
# get
@app.api_route(
    "/gateway/{service}/{path:path}",
    methods=["GET"],
    tags=["Proxy"],
    summary="Proxy to microservices",
    description="Forwards requests to the appropriate downstream microservice based on the service path prefix.",
)
async def proxy(service: str, path: str, request: Request):
    # Resolve the target service URL
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return Response(
            content=f'{{"detail": "Unknown service: {service}"}}',
            status_code=404,
            media_type="application/json",
        )

    # Build the downstream URL
    internal_path = SERVICE_PATH_MAP.get(service, service)
    target_url = f"{base_url}/{internal_path}/{path}".rstrip("/")

    # Forward query parameters
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Read request body
    body = await request.body()

    # Forward headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )

            # Return the downstream response verbatim
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json"),
            )
    except httpx.TimeoutException:
        return Response(
            content='{"detail": "Gateway timeout: downstream service did not respond within 5 seconds"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            content=f'{{"detail": "Service \'{service}\' is unreachable"}}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Gateway error: {str(e)}"}}',
            status_code=500,
            media_type="application/json",
        )
    

#post
@app.api_route(
    "/gateway/{service}/{path:path}",
    methods=["POST"],
    tags=["Proxy"],
    summary="Proxy to microservices",
    description="Forwards requests to the appropriate downstream microservice based on the service path prefix.",
)
async def proxy_post(service: str, path: str, request: Request):
    # Resolve the target service URL
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return Response(
            content=f'{{"detail": "Unknown service: {service}"}}',
            status_code=404,
            media_type="application/json",
        )

    # Build the downstream URL
    internal_path = SERVICE_PATH_MAP.get(service, service)
    target_url = f"{base_url}/{internal_path}/{path}".rstrip("/")

    # Forward query parameters
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Read request body
    body = await request.body()

    # Forward headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )

            # Return the downstream response verbatim
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json"),
            )
    except httpx.TimeoutException:
        return Response(
            content='{"detail": "Gateway timeout: downstream service did not respond within 5 seconds"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            content=f'{{"detail": "Service \'{service}\' is unreachable"}}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Gateway error: {str(e)}"}}',
            status_code=500,
            media_type="application/json",
        ) 

#put
@app.api_route(
    "/gateway/{service}/{path:path}",
    methods=["PUT"],
    tags=["Proxy"],
    summary="Proxy to microservices",
    description="Forwards requests to the appropriate downstream microservice based on the service path prefix.",
)
async def proxy_put(service: str, path: str, request: Request):
    # Resolve the target service URL
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return Response(
            content=f'{{"detail": "Unknown service: {service}"}}',
            status_code=404,
            media_type="application/json",
        )

    # Build the downstream URL
    internal_path = SERVICE_PATH_MAP.get(service, service)
    target_url = f"{base_url}/{internal_path}/{path}".rstrip("/")

    # Forward query parameters
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Read request body
    body = await request.body()

    # Forward headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )

            # Return the downstream response verbatim
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json"),
            )
    except httpx.TimeoutException:
        return Response(
            content='{"detail": "Gateway timeout: downstream service did not respond within 5 seconds"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            content=f'{{"detail": "Service \'{service}\' is unreachable"}}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Gateway error: {str(e)}"}}',
            status_code=500,
            media_type="application/json",
        )

#patch
@app.api_route(
    "/gateway/{service}/{path:path}",
    methods=["PATCH"],
    tags=["Proxy"],
    summary="Proxy to microservices",
    description="Forwards requests to the appropriate downstream microservice based on the service path prefix.",
)
async def proxy_patch(service: str, path: str, request: Request):
    # Resolve the target service URL
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return Response(
            content=f'{{"detail": "Unknown service: {service}"}}',
            status_code=404,
            media_type="application/json",
        )

    # Build the downstream URL
    internal_path = SERVICE_PATH_MAP.get(service, service)
    target_url = f"{base_url}/{internal_path}/{path}".rstrip("/")

    # Forward query parameters
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Read request body
    body = await request.body()

    # Forward headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )

            # Return the downstream response verbatim
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json"),
            )
    except httpx.TimeoutException:
        return Response(
            content='{"detail": "Gateway timeout: downstream service did not respond within 5 seconds"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            content=f'{{"detail": "Service \'{service}\' is unreachable"}}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Gateway error: {str(e)}"}}',
            status_code=500,
            media_type="application/json",
        )

#delete
@app.api_route(
    "/gateway/{service}/{path:path}",
    methods=["DELETE"],
    tags=["Proxy"],
    summary="Proxy to microservices",
    description="Forwards requests to the appropriate downstream microservice based on the service path prefix.",
)
async def proxy_delete(service: str, path: str, request: Request):
    # Resolve the target service URL
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return Response(
            content=f'{{"detail": "Unknown service: {service}"}}',
            status_code=404,
            media_type="application/json",
        )

    # Build the downstream URL
    internal_path = SERVICE_PATH_MAP.get(service, service)
    target_url = f"{base_url}/{internal_path}/{path}".rstrip("/")

    # Forward query parameters
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Read request body
    body = await request.body()

    # Forward headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )

            # Return the downstream response verbatim
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json"),
            )
    except httpx.TimeoutException:
        return Response(
            content='{"detail": "Gateway timeout: downstream service did not respond within 5 seconds"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            content=f'{{"detail": "Service \'{service}\' is unreachable"}}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Gateway error: {str(e)}"}}',
            status_code=500,
            media_type="application/json",
        )   
