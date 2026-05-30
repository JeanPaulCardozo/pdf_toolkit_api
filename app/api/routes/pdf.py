from fastapi import APIRouter, UploadFile, File
from app.services.pdf_service import (
    merge_pdfs,
    extract_text_from_pdf,
    split_pdf,
    convert_pdf_to_word,
    convert_html_to_pdf,
)
from typing import Annotated
from fastapi.responses import Response
from io import BytesIO

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post("/merge")
async def merge_pdf_files(files: Annotated[list[UploadFile], File()]):
    merged_pdf = await merge_pdfs(files)

    return Response(
        content=merged_pdf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"},
    )


@router.post("/extract-text")
async def extract_text_from_pdf_file(file: Annotated[UploadFile, File()]):
    extracted_text = await extract_text_from_pdf(file)

    return {"status": "success", "extracted_text": extracted_text}


@router.post("/split")
async def split_pdf_file(file: Annotated[UploadFile, File()]):
    split_pdfs = await split_pdf(file)

    return Response(
        content=split_pdfs.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=split_pdfs.zip"},
    )


@router.post("/convert-to-word")
async def convert_pdf_to_word_file(file: Annotated[UploadFile, File()]):
    word_file = await convert_pdf_to_word(file)

    return Response(
        content=word_file.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=converted.docx"},
    )


@router.post("/convert-html-to-pdf")
async def convert_html_to_pdf_file(file: UploadFile):

    pdf_file = await convert_html_to_pdf(file)

    return Response(
        content=pdf_file.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=html_to_pdf_converted.pdf"
        },
    )
