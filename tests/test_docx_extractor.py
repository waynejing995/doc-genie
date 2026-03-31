"""Tests for docx_extractor module."""

import pytest


class TestDocxExtractor:
    def test_extract_returns_file_and_sections(self):
        from lib.extractors.docx_extractor import extract_from_docx

        result = extract_from_docx("tests/fixtures/sample.docx")
        assert result["file"] == "tests/fixtures/sample.docx"
        assert "sections" in result

    def test_extract_detects_headings(self):
        from lib.extractors.docx_extractor import extract_from_docx

        result = extract_from_docx("tests/fixtures/sample.docx")
        # Should have at least one heading
        assert any(s.get("level") for s in result["sections"])