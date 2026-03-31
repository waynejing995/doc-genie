"""Tests for CLI module."""

import pytest

from scripts.cli import parse_args


class TestCLI:
    def test_parse_extract_args(self):
        args = parse_args(["extract", "file1.md", "file2.py"])
        assert args.command == "extract"
        assert args.files == ["file1.md", "file2.py"]

    def test_parse_analyze_args(self):
        args = parse_args(["analyze"])
        assert args.command == "analyze"

    def test_parse_report_args(self):
        args = parse_args(["report", "--format", "markdown"])
        assert args.command == "report"
        assert args.format == "markdown"

    def test_parse_report_format_html(self):
        args = parse_args(["report", "--format", "html"])
        assert args.format == "html"

    def test_default_report_format(self):
        args = parse_args(["report"])
        assert args.format == "markdown"
