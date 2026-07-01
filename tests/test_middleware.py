"""Tests for middleware: size limit, security headers, and CORS."""

import io
from tests.conftest import _make_pdf


class TestSecurityHeaders:
    def test_security_headers_present(self, client):
        r = client.get("/health")
        assert r.headers.get("x-content-type-options") == "nosniff"
        assert r.headers.get("x-frame-options") == "DENY"
        assert r.headers.get("referrer-policy") == "no-referrer"
        assert "max-age=63072000" in r.headers.get("strict-transport-security", "")

    def test_server_header_removed(self, client):
        r = client.get("/health")
        assert "server" not in r.headers


class TestSizeLimitMiddleware:
    def test_request_within_size_limit(self, client):
        pdf = _make_pdf(pages=1)
        r = client.post(
            "/pdf/split",
            files=[("file", ("test.pdf", io.BytesIO(pdf), "application/pdf"))],
        )
        assert r.status_code == 200

    def test_oversized_content_length_rejected(self, client):
        """Simulate a request with Content-Length exceeding the limit."""
        r = client.post(
            "/pdf/split",
            content=b"x",
            headers={"content-length": str(21 * 1024 * 1024)},
        )
        assert r.status_code == 413
        assert "too large" in r.json()["detail"].lower()


class TestDocsAvailability:
    """In dev mode (default), /docs should be available."""

    def test_docs_available_in_dev(self, client):
        r = client.get("/docs")
        assert r.status_code == 200

    def test_openapi_json_available(self, client):
        r = client.get("/openapi.json")
        assert r.status_code == 200
        data = r.json()
        assert data["info"]["title"] == "PDF Toolkit API"
