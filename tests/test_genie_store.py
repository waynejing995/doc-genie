"""Tests for genie_store module."""

import pytest


class TestGenieStore:
    def test_init_creates_genie_dir(self, tmp_path):
        from lib.storage.genie_store import GenieStore

        store = GenieStore(str(tmp_path))
        assert (tmp_path / ".genie").exists()

    def test_save_and_load_boxes(self, tmp_path):
        from lib.storage.genie_store import GenieStore

        store = GenieStore(str(tmp_path))
        boxes = [{"id": "bb-001", "name": "Test"}]
        store.save_boxes(boxes)

        loaded = store.load_boxes()
        assert len(loaded) == 1
        assert loaded[0]["id"] == "bb-001"

    def test_update_index(self, tmp_path):
        from lib.storage.genie_store import GenieStore

        store = GenieStore(str(tmp_path))
        boxes = [
            {"id": "bb-001", "name": "Auth", "source": {"file": "auth.py"}},
            {"id": "bb-002", "name": "User", "source": {"file": "user.py"}},
        ]
        store.save_boxes(boxes)

        index = store.load_index()
        assert index["by_name"]["Auth"] == "bb-001"
        assert "auth.py" in index["by_file"]