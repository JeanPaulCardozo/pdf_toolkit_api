from fastapi import FastAPI

app = FastAPI(title="PDF Toolkit API", version="1.0.0")

@app.get("/helth")
async def health_check():
    return {"status": "ok"}