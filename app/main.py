from fastapi import FastAPI

from app.api.routes.pdf import router as pdf_router

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
app = FastAPI(title="PDF Toolkit API", version="1.0.0")

app.include_router(pdf_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
