"""Tests for markdown_extractor module."""

import pytest

from lib.extractors.markdown_extractor import MarkdownExtractor


class TestMarkdownExtractor:
    def test_extract_sections(self):
        md = """
# Title

## Section 1
Some content

## Section 2
More content

### Subsection
Nested content
"""
        extractor = MarkdownExtractor()
        sections = extractor.extract_sections(md)

        assert len(sections) == 4
        assert sections[0]["level"] == 1
        assert sections[1]["level"] == 2
        assert sections[2]["level"] == 2
        assert sections[3]["level"] == 3

    def test_extract_section_content(self):
        md = """
## Auth Service
Handles user authentication.

Input: credentials
Output: JWT token

## Other Service
Does other things.
"""
        extractor = MarkdownExtractor()
        sections = extractor.extract_sections(md)

        auth_section = next(s for s in sections if "Auth" in s["title"])
        assert "credentials" in auth_section["content"].lower()
        assert "jwt" in auth_section["content"].lower()

    def test_extract_io_from_section(self):
        md = """
## Payment Service

Input:
- order_id
- amount

Output:
- payment_result
- receipt
"""
        extractor = MarkdownExtractor()
        sections = extractor.extract_sections(md)
        payment = sections[0]

        io = extractor.extract_io(payment["content"])
        assert "order_id" in io["inputs"]
        assert "amount" in io["inputs"]
        assert "payment_result" in io["outputs"]
        assert "receipt" in io["outputs"]

    def test_extract_from_file(self, tmp_path):
        md = """
# API Spec

## Auth
Input: credentials
Output: token

## Users
Input: user_id
Output: user_data
"""
        filepath = tmp_path / "spec.md"
        filepath.write_text(md)

        extractor = MarkdownExtractor()
        result = extractor.extract_from_file(str(filepath))

        assert result["file"] == str(filepath)
        assert len(result["sections"]) >= 2
