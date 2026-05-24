from fastapi import FastAPI

from app.api.routes.pdf import router as pdf_router

app = FastAPI(title="PDF Toolkit API", version="1.0.0")

app.include_router(pdf_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
