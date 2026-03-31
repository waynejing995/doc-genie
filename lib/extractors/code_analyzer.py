import ast
from pathlib import Path
from typing import Any


class CodeAnalyzer:
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".go": "go",
        ".java": "java",
        ".rb": "ruby",
        ".rs": "rust",
    }

    def _detect_language(self, suffix: str) -> str:
        return self.LANGUAGE_MAP.get(suffix, "unknown")

    def extract_from_file(self, filepath: str) -> dict[str, Any]:
        path = Path(filepath)
        language = self._detect_language(path.suffix)

        if language == "python":
            return self._extract_python(filepath)
        return {
            "file": filepath,
            "language": language,
            "functions": [],
            "classes": [],
            "imports": [],
        }

    def _extract_python(self, filepath: str) -> dict[str, Any]:
        source = Path(filepath).read_text()
        tree = ast.parse(source)

        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [a.arg for a in node.args.args],
                    }
                )
            elif isinstance(node, ast.ClassDef):
                bases = [self._get_name(b) for b in node.bases]
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": bases,
                    }
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({"module": alias.name, "line": node.lineno})
            elif isinstance(node, ast.ImportFrom):
                imports.append(
                    {
                        "module": node.module or "",
                        "names": [a.name for a in node.names],
                        "line": node.lineno,
                    }
                )

        return {
            "file": filepath,
            "language": "python",
            "functions": functions,
            "classes": classes,
            "imports": imports,
        }

    def _get_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)
