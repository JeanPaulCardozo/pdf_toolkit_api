from io import BytesIO

from fastapi import UploadFile, HTTPException

from pypdf import PdfWriter, PdfReader
from pypdf.errors import PdfReadError

from weasyprint import HTML, default_url_fetcher

from pathlib import Path
from tempfile import TemporaryDirectory
from pdf2docx import Converter

from zipfile import ZipFile

from bs4 import BeautifulSoup

import pymupdf
import pymupdf4llm

import logging

logger = logging.getLogger(__name__)


_ALLOWED_SCHEMES = {"data"}


# Helpers
def _safe_url_fetcher(url: str):
    scheme = url.split(":", 1)[0].lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"Blocked external resource: {url}")
    return default_url_fetcher(url)


async def _get_pdf_reader(file: UploadFile) -> tuple[PdfReader, bytes]:
    if file.content_type != "application/pdf":
        logger.error(
            f"Unsupported file type: {file.content_type} for file {file.filename}"
        )
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_bytes = await file.read()

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="File is not a valid PDF")

    try:
        reader = PdfReader(BytesIO(pdf_bytes))

        if reader.is_encrypted:
            logger.error(f"Encrypted PDF detected: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Encrypted PDF files are not supported: {file.filename}",
            )

    except PdfReadError:
        logger.error(f"Invalid PDF detected: {file.filename}")
        raise HTTPException(
            status_code=400, detail=f"Invalid or corrupted PDF :{file.filename}"
        )

    return reader, pdf_bytes


# Functions
async def merge_pdfs(files: list[UploadFile]) -> BytesIO:
    writer = PdfWriter()

    for file in files:
        logger.info(f"Processing file: {file.filename}")

        reader, _ = await _get_pdf_reader(file)

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()

    writer.write(output)
    output.seek(0)

    logger.info("PDF merge completed successfully")

    return output


async def extract_text_from_pdf(file: UploadFile) -> str:
    logger.info(f"Processing file: {file.filename}")

    reader, _ = await _get_pdf_reader(file)

    extracted_text = ""

    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    logger.info(f"Text extraction completed successfully for file: {file.filename}")

    return extracted_text


async def split_pdf_by_range(
    file: UploadFile, ranges: list[tuple[int, int]]
) -> BytesIO:
    logger.info(f"Processing file {file.filename}")

    reader, _ = await _get_pdf_reader(file)
    total_pages = len(reader.pages)

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        for page_range in ranges:
            start = page_range.start
            end = page_range.end
            if start < 1 or end < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Page ranges must start from page 1",
                )

            if start > end:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid range: {start}-{end}",
                )

            if end > total_pages:
                raise HTTPException(
                    status_code=400,
                    detail=f"Range {start}-{end} exceeds the total number of pages: {total_pages}",
                )

            writer = PdfWriter()

            for page_number in range(start, end + 1):
                writer.add_page(reader.pages[page_number - 1])

            pdf_buffer = BytesIO()
            writer.write(pdf_buffer)
            zip_file.writestr(f"pages_{start}_to_{end}.pdf", pdf_buffer.getvalue())

    zip_buffer.seek(0)
    logger.info(f"PDF split completed successfully for file: {file.filename}")

    return zip_buffer


async def split_pdf(file: UploadFile) -> BytesIO:
    logger.info(f"Processing file: {file.filename}")

    reader, _ = await _get_pdf_reader(file)

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        for index, page in enumerate(reader.pages):
            writer = PdfWriter()

            writer.add_page(page)

            pdf_buffer = BytesIO()
            writer.write(pdf_buffer)

            zip_file.writestr(f"page_{index + 1}.pdf", pdf_buffer.getvalue())

    zip_buffer.seek(0)
    logger.info(f"PDF split completed successfully for file: {file.filename}")

    return zip_buffer


async def convert_pdf_to_word(file: UploadFile) -> BytesIO:

    logger.info("Starting PDF to Word conversion")

    _, pdf_bytes = await _get_pdf_reader(file)

    try:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            pdf_path = temp_path / "input.pdf"
            docx_path = temp_path / "output.docx"

            pdf_path.write_bytes(pdf_bytes)

            converter = Converter(str(pdf_path))
            try:
                converter.convert(str(docx_path))
            except Exception as error:
                logger.exception("PDF to Word conversion failed")
                raise HTTPException(status_code=400, detail=str(error))
            finally:
                converter.close()

            word_buffer = BytesIO(docx_path.read_bytes())
            word_buffer.seek(0)

        logger.info("PDF to Word conversion completed successfully")
        return word_buffer
    except Exception as error:
        logger.error(f"PDF to Word conversion failed: {error}")
        raise HTTPException(status_code=400, detail=str(error))


async def convert_html_to_pdf(file: UploadFile) -> BytesIO:
    logger.info("Starting HTML to PDF conversion")

    if file.content_type != "text/html":
        logger.error(
            f"Unsupported file type: {file.content_type} for file {file.filename}"
        )
        raise HTTPException(status_code=400, detail="Only HTML files are allowed")

    file_content = await file.read()

    try:
        html_content = file_content.decode("utf-8")
    except UnicodeDecodeError, LookupError:
        logger.error(f"Invalid text encoding for file: {file.filename}")
        raise HTTPException(
            status_code=400, detail="The uploaded file content is not valid HTML"
        )

    soup = BeautifulSoup(html_content, "html.parser")

    is_valid_html = soup.find("html") is not None and soup.find("body") is not None

    if not is_valid_html:
        logger.error(f"Invalid HTML content detected: {file.filename}")
        raise HTTPException(
            status_code=400, detail="The uploaded file content is not valid HTML"
        )

    pdf_buffer = BytesIO()

    HTML(string=html_content, url_fetcher=_safe_url_fetcher).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    logger.info("HTML to PDF conversion completed successfully")
    return pdf_buffer


async def convert_pdf_to_md(file: UploadFile) -> BytesIO:
    logger.info("Starting PDF to Markdown conversion")
    _, pdf_bytes = await _get_pdf_reader(file)

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    markdown = pymupdf4llm.to_markdown(doc)

    md_file_buffer = BytesIO(markdown.encode("utf-8"))
    md_file_buffer.seek(0)

    logger.info("PDF to Markdown conversion completed successfully")

    return md_file_buffer
