"""Tests for tree_sitter_extractor module."""

import pytest


class TestTreeSitterExtractor:
    def test_extract_python_functions(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.py")
        assert result["language"] == "python"
        assert any(f["name"] == "hello" for f in result["functions"])

    def test_extract_python_classes(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.py")
        assert any(c["name"] == "UserService" for c in result["classes"])

    def test_extract_python_imports(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.py")
        assert any(i["module"] == "os" for i in result["imports"])

    def test_unsupported_language_returns_error(self):
        from lib.extractors.tree_sitter_extractor import extract_structure

        result = extract_structure("tests/fixtures/sample.xyz")
        assert "error" in result