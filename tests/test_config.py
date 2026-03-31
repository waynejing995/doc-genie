"""Tests for config module."""

import pytest
from pathlib import Path


class TestGenieConfig:
    def test_default_config(self, tmp_path):
        from lib.config import GenieConfig

        config = GenieConfig(str(tmp_path))
        assert config.depth == "medium"
        assert config.depth_profiles["medium"]["confidence_threshold"] == 0.7

    def test_load_user_config(self, tmp_path):
        from lib.config import GenieConfig

        genie_dir = tmp_path / ".genie"
        genie_dir.mkdir()
        (genie_dir / "config.yaml").write_text("depth: deep\n")

        config = GenieConfig(str(tmp_path))
        assert config.depth == "deep"

    def test_should_process_file(self, tmp_path):
        from lib.config import GenieConfig

        config = GenieConfig(str(tmp_path))
        assert config.should_process_file("test.py") is True
        assert config.should_process_file("test.xyz") is False

    def test_box_size_thresholds(self, tmp_path):
        from lib.config import GenieConfig

        config = GenieConfig(str(tmp_path))
        assert config.box_size_thresholds["quick"]["min_lines"] == 20
        assert config.box_size_thresholds["deep"]["min_lines"] == 1