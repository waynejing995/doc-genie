"""Tests for CLI module."""

import pytest


class TestCLI:
    def test_parse_extract_args(self):
        from scripts.cli import parse_args

        args = parse_args(["extract", "file1.md", "file2.py"])
        assert args.command == "extract"
        assert args.files == ["file1.md", "file2.py"]

    def test_parse_extract_with_depth(self):
        from scripts.cli import parse_args

        args = parse_args(["extract", "file.py", "--depth", "deep"])
        assert args.depth == "deep"

    def test_parse_init_args(self):
        from scripts.cli import parse_args

        args = parse_args(["init"])
        assert args.command == "init"

    def test_parse_config_args(self):
        from scripts.cli import parse_args

        args = parse_args(["config", "show"])
        assert args.command == "config"
        assert args.action == "show"

    def test_parse_report_args(self):
        from scripts.cli import parse_args

        args = parse_args(["report", "--format", "html"])
        assert args.command == "report"
        assert args.format == "html"

    def test_parse_report_format_html(self):
        from scripts.cli import parse_args

        args = parse_args(["report", "--format", "html"])
        assert args.format == "html"

    def test_default_report_format(self):
        from scripts.cli import parse_args

        args = parse_args(["report"])
        assert args.format == "markdown"

    def test_default_depth_uses_config(self, tmp_path, monkeypatch):
        from scripts.cli import extract

        monkeypatch.chdir(tmp_path)
        # Create a sample file
        sample_py = tmp_path / "sample.py"
        sample_py.write_text("def hello(): pass\n")

        results = extract([str(sample_py)], output="json")
        # Default depth should be "medium"
        assert results[0]["_depth"] == "medium"