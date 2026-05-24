from io import BytesIO

from fastapi import UploadFile, HTTPException

from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError



async def merge_pdfs(files: list[UploadFile]) -> bytes:
    writer = PdfWriter()

    for file in files:

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        pdf_bytes = await file.read()
        pdf_stream = BytesIO(pdf_bytes)

        try:
            reader = PdfReader(pdf_stream)

        except PdfReadError:
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted PDF :{file.filename}")

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()

    writer.write(output)
    output.seek(0)

    return output.getvalue()
