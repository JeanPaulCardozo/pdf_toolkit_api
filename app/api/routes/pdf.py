from fastapi import APIRouter, UploadFile, File
from app.services.pdf_service import merge_pdfs
from typing import Annotated
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post("/merge")
async def merge_pdf_files(files: Annotated[list[UploadFile], File()]):
    merged_pdf = await merge_pdfs(files)

    return StreamingResponse(
        content=BytesIO(merged_pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"},
    )
