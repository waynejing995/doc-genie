"""Project configuration management."""

import yaml
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "version": "1.0",
    "depth": "medium",
    "box_size_thresholds": {
        "quick": {"min_lines": 20, "min_chars": 300},
        "medium": {"min_lines": 5, "min_chars": 100},
        "deep": {"min_lines": 1, "min_chars": 30},
    },
    "depth_profiles": {
        "quick": {
            "extract_comments": False,
            "extract_signatures": True,
            "detect_implicit": False,
            "confidence_threshold": 0.8,
        },
        "medium": {
            "extract_comments": False,
            "extract_signatures": True,
            "detect_implicit": False,
            "confidence_threshold": 0.7,
        },
        "deep": {
            "extract_comments": True,
            "extract_signatures": True,
            "detect_implicit": True,
            "confidence_threshold": 0.6,
        },
    },
    "file_types": [".md", ".py", ".js", ".ts", ".c", ".h", ".pdf", ".docx"],
    "exclude_patterns": ["node_modules/**", ".venv/**", "**/__pycache__/**"],
    "output": {"format": "yaml", "language": "auto"},
}


class GenieConfig:
    """Project-level configuration for BoxMatrix."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / ".boxmatrix" / "config.yaml"
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            user_config = yaml.safe_load(self.config_file.read_text())
            if user_config:
                return self._merge_config(DEFAULT_CONFIG.copy(), user_config)
        return DEFAULT_CONFIG.copy()

    def _merge_config(self, default: dict, user: dict) -> dict:
        """Deep merge user config into defaults."""
        result = default.copy()
        for key, value in user.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    @property
    def depth(self) -> str:
        """Current extraction depth."""
        return self._config.get("depth", "medium")

    @property
    def depth_profiles(self) -> dict:
        """Depth profile settings."""
        return self._config.get("depth_profiles", {})

    @property
    def box_size_thresholds(self) -> dict:
        """Box size thresholds by depth."""
        return self._config.get("box_size_thresholds", {})

    @property
    def file_types(self) -> list[str]:
        """Supported file types."""
        return self._config.get("file_types", [])

    @property
    def exclude_patterns(self) -> list[str]:
        """Patterns to exclude."""
        return self._config.get("exclude_patterns", [])

    def should_process_file(self, filepath: str) -> bool:
        """Check if file should be processed based on config."""
        path = Path(filepath)

        # Check file type
        if path.suffix not in self.file_types:
            return False

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if path.match(pattern.replace("**/", "")):
                return False

        return True

    def get_depth_profile(self, depth: str | None = None) -> dict:
        """Get settings for a specific depth level."""
        depth = depth or self.depth
        return self.depth_profiles.get(depth, self.depth_profiles["medium"])

    def get_box_threshold(self, depth: str | None = None) -> dict:
        """Get box size threshold for a specific depth."""
        depth = depth or self.depth
        return self.box_size_thresholds.get(depth, self.box_size_thresholds["medium"])