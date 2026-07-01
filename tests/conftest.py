import io
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _make_pdf(pages: int = 1, text_per_page: list[str] | None = None) -> bytes:
    """Generate a minimal valid PDF with the given number of pages."""
    writer = PdfWriter()
    if text_per_page is None:
        text_per_page = [f"Page {i + 1} content" for i in range(pages)]
    for txt in text_per_page:
        writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.fixture
def sample_pdf_bytes():
    return _make_pdf(pages=3)


@pytest.fixture
def single_page_pdf_bytes():
    return _make_pdf(pages=1)


@pytest.fixture
def html_bytes():
    return b"<!DOCTYPE html><html><body><h1>Hello</h1><p>Test</p></body></html>"


@pytest.fixture
def invalid_html_bytes():
    return b"not html at all"


@pytest.fixture
def non_pdf_bytes():
    return b"This is not a PDF file"
