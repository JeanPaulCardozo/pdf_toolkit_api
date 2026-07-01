"""Unit tests for service functions."""

import io
import json
import zipfile

import pytest
from fastapi import UploadFile, HTTPException

from app.services.pdf_service import (
    merge_pdfs,
    extract_text_from_pdf,
    split_pdf,
    split_pdf_by_range,
    convert_pdf_to_word,
    convert_html_to_pdf,
    convert_pdf_to_md,
    _get_pdf_reader,
    _safe_url_fetcher,
)
from app.schemas.pdf_schemas import PageRange
from tests.conftest import _make_pdf


def _upload(
    data: bytes, filename: str = "test.pdf", content_type: str = "application/pdf"
) -> UploadFile:
    return UploadFile(
        file=io.BytesIO(data), filename=filename, headers={"content-type": content_type}
    )


# ── _get_pdf_reader ─────────────────────────────────────────────────────────


class TestGetPdfReader:
    @pytest.mark.asyncio
    async def test_valid_pdf(self):
        pdf = _make_pdf(1)
        reader, raw = await _get_pdf_reader(_upload(pdf))
        assert len(reader.pages) == 1

    @pytest.mark.asyncio
    async def test_wrong_content_type(self):
        with pytest.raises(HTTPException) as exc_info:
            await _get_pdf_reader(_upload(b"data", content_type="text/plain"))
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_not_a_real_pdf(self):
        with pytest.raises(HTTPException) as exc_info:
            await _get_pdf_reader(_upload(b"not-pdf", content_type="application/pdf"))
        assert exc_info.value.status_code == 400


# ── _safe_url_fetcher ───────────────────────────────────────────────────────


class TestSafeUrlFetcher:
    def test_blocks_http(self):
        with pytest.raises(ValueError, match="Blocked"):
            _safe_url_fetcher("http://evil.com/img.png")

    def test_blocks_file(self):
        with pytest.raises(ValueError, match="Blocked"):
            _safe_url_fetcher("file:///etc/passwd")

    def test_allows_data_scheme(self):
        # data: scheme should not raise ValueError (blocked), but may raise
        # other errors (e.g. invalid base64 padding) which are acceptable.
        try:
            _safe_url_fetcher("data:image/png;base64,abc")
        except ValueError as e:
            if "Blocked" in str(e):
                pytest.fail("data: scheme should not be blocked")
            # ValueError not related to blocking is fine
        except Exception:
            pass  # other errors are fine (e.g. invalid base64)


# ── merge_pdfs ──────────────────────────────────────────────────────────────


class TestMergePdfs:
    @pytest.mark.asyncio
    async def test_merge_returns_valid_pdf(self):
        pdf1 = _make_pdf(2)
        pdf2 = _make_pdf(3)
        result = await merge_pdfs([_upload(pdf1), _upload(pdf2)])
        assert result.read(5) == b"%PDF-"

    @pytest.mark.asyncio
    async def test_merge_preserves_page_count(self):
        from pypdf import PdfReader

        pdf1 = _make_pdf(2)
        pdf2 = _make_pdf(3)
        result = await merge_pdfs([_upload(pdf1), _upload(pdf2)])
        reader = PdfReader(result)
        assert len(reader.pages) == 5


# ── extract_text_from_pdf ───────────────────────────────────────────────────


class TestExtractText:
    @pytest.mark.asyncio
    async def test_returns_string(self):
        pdf = _make_pdf(1)
        text = await extract_text_from_pdf(_upload(pdf))
        assert isinstance(text, str)

    @pytest.mark.asyncio
    async def test_rejects_non_pdf(self):
        with pytest.raises(HTTPException):
            await extract_text_from_pdf(_upload(b"x", content_type="text/plain"))


# ── split_pdf ───────────────────────────────────────────────────────────────


class TestSplitPdf:
    @pytest.mark.asyncio
    async def test_split_produces_zip_with_correct_count(self):
        pdf = _make_pdf(4)
        result = await split_pdf(_upload(pdf))
        zf = zipfile.ZipFile(result)
        assert len(zf.namelist()) == 4

    @pytest.mark.asyncio
    async def test_each_zip_entry_is_pdf(self):
        pdf = _make_pdf(2)
        result = await split_pdf(_upload(pdf))
        zf = zipfile.ZipFile(result)
        for name in zf.namelist():
            assert zf.read(name).startswith(b"%PDF-")


# ── split_pdf_by_range ──────────────────────────────────────────────────────


class TestSplitPdfByRange:
    @pytest.mark.asyncio
    async def test_valid_ranges(self):
        pdf = _make_pdf(5)
        ranges = [PageRange(start=1, end=2), PageRange(start=4, end=5)]
        result = await split_pdf_by_range(_upload(pdf), ranges)
        zf = zipfile.ZipFile(result)
        assert len(zf.namelist()) == 2

    @pytest.mark.asyncio
    async def test_range_exceeds_pages(self):
        pdf = _make_pdf(2)
        ranges = [PageRange(start=1, end=10)]
        with pytest.raises(HTTPException) as exc_info:
            await split_pdf_by_range(_upload(pdf), ranges)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_start_greater_than_end(self):
        pdf = _make_pdf(3)
        ranges = [PageRange(start=3, end=1)]
        with pytest.raises(HTTPException) as exc_info:
            await split_pdf_by_range(_upload(pdf), ranges)
        assert exc_info.value.status_code == 400


# ── convert_pdf_to_word ─────────────────────────────────────────────────────


class TestConvertPdfToWord:
    @pytest.mark.asyncio
    async def test_returns_docx(self):
        pdf = _make_pdf(1)
        result = await convert_pdf_to_word(_upload(pdf))
        data = result.read()
        # docx files are ZIP-based; check magic bytes
        assert data[:2] == b"PK"


# ── convert_html_to_pdf ─────────────────────────────────────────────────────


class TestConvertHtmlToPdf:
    @pytest.mark.asyncio
    async def test_valid_html(self):
        html = b"<!DOCTYPE html><html><body><p>Hi</p></body></html>"
        result = await convert_html_to_pdf(
            _upload(html, filename="p.html", content_type="text/html")
        )
        assert result.read(5) == b"%PDF-"

    @pytest.mark.asyncio
    async def test_rejects_non_html_content_type(self):
        with pytest.raises(HTTPException) as exc_info:
            await convert_html_to_pdf(_upload(b"hi", content_type="text/plain"))
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_rejects_invalid_html_body(self):
        with pytest.raises(HTTPException) as exc_info:
            await convert_html_to_pdf(
                _upload(b"no tags", filename="p.html", content_type="text/html")
            )
        assert exc_info.value.status_code == 400


# ── convert_pdf_to_md ───────────────────────────────────────────────────────


class TestConvertPdfToMd:
    @pytest.mark.asyncio
    async def test_returns_markdown(self):
        pdf = _make_pdf(1)
        result = await convert_pdf_to_md(_upload(pdf))
        md = result.read().decode("utf-8")
        assert isinstance(md, str)

    @pytest.mark.asyncio
    async def test_rejects_non_pdf(self):
        with pytest.raises(HTTPException):
            await convert_pdf_to_md(_upload(b"x", content_type="text/plain"))
