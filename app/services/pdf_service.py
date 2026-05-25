from io import BytesIO

from fastapi import UploadFile, HTTPException

from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError

from zipfile import ZipFile

import logging

logger = logging.getLogger(__name__)


async def _get_pdf_reader(file: UploadFile) -> PdfReader:
    if file.content_type != "application/pdf":
        logger.error(
            f"Unsupported file type: {file.content_type} for file {file.filename}"
        )
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_bytes = await file.read()
    pdf_stream = BytesIO(pdf_bytes)

    try:
        reader = PdfReader(pdf_stream)

    except PdfReadError:
        logger.error(f"Invalid PDF detected: {file.filename}")
        raise HTTPException(
            status_code=400, detail=f"Invalid or corrupted PDF :{file.filename}"
        )

    return reader


async def merge_pdfs(files: list[UploadFile]) -> bytes:
    writer = PdfWriter()

    for file in files:
        logger.info(f"Processing file: {file.filename}")

        reader = await _get_pdf_reader(file)

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()

    writer.write(output)
    output.seek(0)

    logger.info("PDF merge completed successfully")

    return output.getvalue()


async def extract_text_from_pdf(file: UploadFile) -> str:
    logger.info(f"Processing file: {file.filename}")

    reader = await _get_pdf_reader(file)

    extracted_text = ""

    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    logger.info(f"Text extraction completed successfully for file: {file.filename}")

    return extracted_text


async def split_pdf(file: UploadFile) -> bytes:
    logger.info(f"Processing file: {file.filename}")

    reader = await _get_pdf_reader(file)

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        for index, page in enumerate(reader.pages):
            writer = PdfWriter()

            writer.add_page(page)

            pdf_buffer = BytesIO()
            writer.write(pdf_buffer)

            zip_file.writestr(f"page_{index + 1}.pdf", pdf_buffer.getvalue())

    zip_buffer.seek(0)

    return zip_buffer.getvalue()
