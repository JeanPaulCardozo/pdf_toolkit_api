import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.pdf import router as pdf_router

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

DEBUG = os.getenv("ENV", "development") != "production"
MAX_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 20 * 1024 * 1024))  # 20 MB
app = FastAPI(
    title="PDF Toolkit API",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
)

# --- CORS ---
allowed = os.getenv("ALLOWED_ORIGINS", "")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in allowed.split(",") if o],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Size Limit ---
@app.middleware("http")
async def limit_upload_size(request, call_next):
    cl = request.headers.get("content-length")
    if cl and int(cl) > MAX_BYTES:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Payload too large (max {MAX_BYTES} bytes)"},
        )
    return await call_next(request)


# --- Security Headers ---
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains"
    )
    if "server" in response.headers:
        del response.headers["server"]
    return response


app.include_router(pdf_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
