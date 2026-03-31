"""Tests for code_analyzer module."""

import pytest
import tempfile
from pathlib import Path

from lib.extractors.code_analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    def test_detect_language(self):
        analyzer = CodeAnalyzer()
        assert analyzer._detect_language(".py") == "python"
        assert analyzer._detect_language(".js") == "javascript"
        assert analyzer._detect_language(".ts") == "typescript"
        assert analyzer._detect_language(".go") == "go"
        assert analyzer._detect_language(".java") == "java"
        assert analyzer._detect_language(".xyz") == "unknown"

    def test_extract_python_functions(self, tmp_path):
        code = """
def hello(name: str) -> str:
    return f"Hello {name}"

def add(a: int, b: int) -> int:
    return a + b
"""
        filepath = tmp_path / "test.py"
        filepath.write_text(code)

        analyzer = CodeAnalyzer()
        result = analyzer.extract_from_file(str(filepath))

        assert result["language"] == "python"
        assert len(result["functions"]) == 2
        assert "hello" in [f["name"] for f in result["functions"]]
        assert "add" in [f["name"] for f in result["functions"]]

    def test_extract_python_classes(self, tmp_path):
        code = """
class UserService:
    def get_user(self, user_id: str):
        pass

class AuthService(UserService):
    def authenticate(self, credentials):
        pass
"""
        filepath = tmp_path / "test.py"
        filepath.write_text(code)

        analyzer = CodeAnalyzer()
        result = analyzer.extract_from_file(str(filepath))

        assert len(result["classes"]) == 2
        class_names = [c["name"] for c in result["classes"]]
        assert "UserService" in class_names
        assert "AuthService" in class_names

    def test_extract_python_imports(self, tmp_path):
        code = """
import os
from typing import List, Dict
from lib.models import User, Auth
"""
        filepath = tmp_path / "test.py"
        filepath.write_text(code)

        analyzer = CodeAnalyzer()
        result = analyzer.extract_from_file(str(filepath))

        assert len(result["imports"]) >= 3

    def test_extract_from_dict(self, tmp_path):
        code = """
def process(data: dict) -> list:
    return list(data.values())
"""
        filepath = tmp_path / "test.py"
        filepath.write_text(code)

        analyzer = CodeAnalyzer()
        result = analyzer.extract_from_file(str(filepath))

        assert result["file"] == str(filepath)
        assert result["language"] == "python"
        assert "functions" in result
        assert "classes" in result
        assert "imports" in result
