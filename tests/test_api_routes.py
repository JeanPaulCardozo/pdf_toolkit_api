"""Tests for all PDF API endpoints."""

import json
import io
import zipfile

from tests.conftest import _make_pdf


# ── Health ──────────────────────────────────────────────────────────────────


class TestHealthCheck:
    def test_health_returns_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ── /pdf/merge ──────────────────────────────────────────────────────────────


class TestMergePDFs:
    def test_merge_two_pdfs(self, client):
        pdf1 = _make_pdf(pages=2)
        pdf2 = _make_pdf(pages=3)
        r = client.post(
            "/pdf/merge",
            files=[
                ("files", ("a.pdf", io.BytesIO(pdf1), "application/pdf")),
                ("files", ("b.pdf", io.BytesIO(pdf2), "application/pdf")),
            ],
        )
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert "merged.pdf" in r.headers.get("content-disposition", "")

    def test_merge_single_pdf(self, client):
        pdf = _make_pdf(pages=1)
        r = client.post(
            "/pdf/merge",
            files=[("files", ("a.pdf", io.BytesIO(pdf), "application/pdf"))],
        )
        assert r.status_code == 200

    def test_merge_rejects_non_pdf(self, client):
        r = client.post(
            "/pdf/merge",
            files=[("files", ("a.txt", io.BytesIO(b"hello"), "text/plain"))],
        )
        assert r.status_code == 400

    def test_merge_rejects_fake_pdf(self, client):
        r = client.post(
            "/pdf/merge",
            files=[
                ("files", ("fake.pdf", io.BytesIO(b"not a pdf"), "application/pdf"))
            ],
        )
        assert r.status_code == 400


# ── /pdf/extract-text ──────────────────────────────────────────────────────


class TestExtractText:
    def test_extract_text_from_pdf(self, client):
        pdf = _make_pdf(pages=1)
        r = client.post(
            "/pdf/extract-text",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "success"
        assert "extracted_text" in body

    def test_extract_text_rejects_non_pdf(self, client):
        r = client.post(
            "/pdf/extract-text",
            files=[("file", ("test.txt", io.BytesIO(b"data"), "text/plain"))],
        )
        assert r.status_code == 400


# ── /pdf/split ──────────────────────────────────────────────────────────────


class TestSplitPDF:
    def test_split_multipage_pdf(self, client):
        pdf = _make_pdf(pages=3)
        r = client.post(
            "/pdf/split",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
        )
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/zip"

        zf = zipfile.ZipFile(io.BytesIO(r.content))
        names = zf.namelist()
        assert len(names) == 3
        assert "page_1.pdf" in names
        assert "page_2.pdf" in names
        assert "page_3.pdf" in names

    def test_split_single_page_pdf(self, client):
        pdf = _make_pdf(pages=1)
        r = client.post(
            "/pdf/split",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
        )
        assert r.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        assert len(zf.namelist()) == 1

    def test_split_rejects_non_pdf(self, client):
        r = client.post(
            "/pdf/split",
            files=[("file", ("test.txt", io.BytesIO(b"data"), "text/plain"))],
        )
        assert r.status_code == 400


# ── /pdf/split_by_ranges ────────────────────────────────────────────────────


class TestSplitByRanges:
    def test_split_by_valid_ranges(self, client):
        pdf = _make_pdf(pages=5)
        ranges = json.dumps([{"start": 1, "end": 2}, {"start": 3, "end": 5}])
        r = client.post(
            "/pdf/split_by_ranges",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
            data={"ranges": ranges},
        )
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/zip"

        zf = zipfile.ZipFile(io.BytesIO(r.content))
        names = zf.namelist()
        assert len(names) == 2
        assert "pages_1_to_2.pdf" in names
        assert "pages_3_to_5.pdf" in names

    def test_split_by_ranges_invalid_json(self, client):
        pdf = _make_pdf(pages=2)
        r = client.post(
            "/pdf/split_by_ranges",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
            data={"ranges": "not-json"},
        )
        assert r.status_code == 400

    def test_split_by_ranges_invalid_schema(self, client):
        pdf = _make_pdf(pages=2)
        ranges = json.dumps([{"start": 0, "end": -1}])
        r = client.post(
            "/pdf/split_by_ranges",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
            data={"ranges": ranges},
        )
        assert r.status_code == 422

    def test_split_by_ranges_exceeds_total_pages(self, client):
        pdf = _make_pdf(pages=2)
        ranges = json.dumps([{"start": 1, "end": 10}])
        r = client.post(
            "/pdf/split_by_ranges",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
            data={"ranges": ranges},
        )
        assert r.status_code == 400

    def test_split_by_ranges_start_greater_than_end(self, client):
        pdf = _make_pdf(pages=3)
        ranges = json.dumps([{"start": 3, "end": 1}])
        r = client.post(
            "/pdf/split_by_ranges",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
            data={"ranges": ranges},
        )
        assert r.status_code == 400


# ── /pdf/convert-to-word ────────────────────────────────────────────────────


class TestConvertToWord:
    def test_convert_pdf_to_word(self, client):
        pdf = _make_pdf(pages=1)
        r = client.post(
            "/pdf/convert-to-word",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
        )
        assert r.status_code == 200
        assert "wordprocessingml" in r.headers["content-type"]
        assert "converted.docx" in r.headers.get("content-disposition", "")

    def test_convert_to_word_rejects_non_pdf(self, client):
        r = client.post(
            "/pdf/convert-to-word",
            files=[("file", ("test.txt", io.BytesIO(b"data"), "text/plain"))],
        )
        assert r.status_code == 400


# ── /pdf/convert-html-to-pdf ───────────────────────────────────────────────


class TestConvertHtmlToPdf:
    def test_convert_valid_html(self, client, html_bytes):
        r = client.post(
            "/pdf/convert-html-to-pdf",
            files=[("file", ("page.html", io.BytesIO(html_bytes), "text/html"))],
        )
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"

    def test_convert_rejects_non_html_content_type(self, client):
        r = client.post(
            "/pdf/convert-html-to-pdf",
            files=[("file", ("page.txt", io.BytesIO(b"hello"), "text/plain"))],
        )
        assert r.status_code == 400

    def test_convert_rejects_invalid_html_content(self, client, invalid_html_bytes):
        r = client.post(
            "/pdf/convert-html-to-pdf",
            files=[
                ("file", ("page.html", io.BytesIO(invalid_html_bytes), "text/html"))
            ],
        )
        assert r.status_code == 400


# ── /pdf/convert-pdf-to-md ─────────────────────────────────────────────────


class TestConvertPdfToMd:
    def test_convert_pdf_to_markdown(self, client):
        pdf = _make_pdf(pages=1)
        r = client.post(
            "/pdf/convert-pdf-to-md",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
        )
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/markdown")
        assert "pdf_to_md_converted.md" in r.headers.get("content-disposition", "")

    def test_convert_pdf_to_md_rejects_non_pdf(self, client):
        r = client.post(
            "/pdf/convert-pdf-to-md",
            files=[("file", ("test.txt", io.BytesIO(b"data"), "text/plain"))],
        )
        assert r.status_code == 400
