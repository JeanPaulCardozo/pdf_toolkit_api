from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfWriter, PdfReader


async def merge_pdfs(files: list[UploadFile]) -> bytes:
    writer = PdfWriter()

    for file in files:
        pdf_bytes = await file.read()
        pdf_stream = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()

    writer.write(output)
    output.seek(0)

    return output.getvalue()
