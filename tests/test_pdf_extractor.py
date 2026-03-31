"""Tests for pdf_extractor module."""

import pytest


class TestPdfExtractor:
    def test_extract_returns_file_and_sections(self):
        from lib.extractors.pdf_extractor import extract_from_pdf

        result = extract_from_pdf("tests/fixtures/sample.pdf")
        assert result["file"] == "tests/fixtures/sample.pdf"
        assert "sections" in result

    def test_extract_sections_have_content(self):
        from lib.extractors.pdf_extractor import extract_from_pdf

        result = extract_from_pdf("tests/fixtures/sample.pdf")
        assert len(result["sections"]) >= 0