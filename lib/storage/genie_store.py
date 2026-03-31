"""Persistent storage for doc-genie analysis results."""

import json
from pathlib import Path
from typing import Any


class GenieStore:
    """Persistent storage for black boxes, relationships, and analysis results."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.genie_dir = self.project_root / ".genie"
        self.genie_dir.mkdir(exist_ok=True)

        self.boxes_file = self.genie_dir / "boxes.json"
        self.rels_file = self.genie_dir / "relationships.json"
        self.patterns_file = self.genie_dir / "patterns.json"
        self.review_file = self.genie_dir / "review.json"
        self.index_file = self.genie_dir / "index.json"

    def load_boxes(self) -> list[dict]:
        """Load black boxes from storage."""
        if self.boxes_file.exists():
            data = json.loads(self.boxes_file.read_text())
            return data.get("boxes", [])
        return []

    def save_boxes(self, boxes: list[dict], metadata: dict | None = None):
        """Save black boxes to storage."""
        data = {
            "version": "1.0",
            "generated_at": self._get_timestamp(),
            "boxes": boxes,
        }
        if metadata:
            data["metadata"] = metadata

        self.boxes_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        self._update_index(boxes)

    def load_relationships(self) -> list[dict]:
        """Load relationships from storage."""
        if self.rels_file.exists():
            data = json.loads(self.rels_file.read_text())
            return data.get("relationships", [])
        return []

    def save_relationships(self, relationships: list[dict], metadata: dict | None = None):
        """Save relationships to storage."""
        data = {
            "version": "1.0",
            "generated_at": self._get_timestamp(),
            "relationships": relationships,
        }
        if metadata:
            data["metadata"] = metadata

        self.rels_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def load_patterns(self) -> list[dict]:
        """Load detected patterns from storage."""
        if self.patterns_file.exists():
            data = json.loads(self.patterns_file.read_text())
            return data.get("patterns", [])
        return []

    def save_patterns(self, patterns: list[dict]):
        """Save detected patterns to storage."""
        data = {
            "version": "1.0",
            "generated_at": self._get_timestamp(),
            "patterns": patterns,
        }
        self.patterns_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def load_review(self) -> dict:
        """Load review status from storage."""
        if self.review_file.exists():
            return json.loads(self.review_file.read_text())
        return {"version": "1.0", "pending_review": [], "disputed": []}

    def save_review(self, review: dict):
        """Save review status to storage."""
        review["version"] = "1.0"
        self.review_file.write_text(json.dumps(review, indent=2, ensure_ascii=False))

    def load_index(self) -> dict:
        """Load search index from storage."""
        if self.index_file.exists():
            return json.loads(self.index_file.read_text())
        return {"by_name": {}, "by_file": {}, "by_keyword": {}}

    def _update_index(self, boxes: list[dict]):
        """Update search index after saving boxes."""
        index = {
            "by_name": {},
            "by_file": {},
            "by_keyword": {},
        }

        for box in boxes:
            # Index by name
            name = box.get("name", "")
            if name:
                index["by_name"][name] = box["id"]

            # Index by file
            source = box.get("source", {})
            file = source.get("file", "")
            if file:
                if file not in index["by_file"]:
                    index["by_file"][file] = []
                index["by_file"][file].append(box["id"])

        self.index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()