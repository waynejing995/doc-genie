"""PDF extractor using pdfplumber."""

import re
from pathlib import Path
from typing import Any

import pdfplumber


def extract_from_pdf(filepath: str) -> dict[str, Any]:
    """Extract structured content from PDF."""
    sections = []
    current_section = None
    current_content = []
    total_pages = 0

    with pdfplumber.open(filepath) as pdf:
        total_pages = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            for line in lines:
                # Detect headings (larger font, numbered, or all caps)
                if _is_heading(line):
                    if current_section:
                        current_section["content"] = "\n".join(current_content)
                        sections.append(current_section)
                    current_section = {
                        "title": line.strip(),
                        "page": page_num,
                        "level": _detect_heading_level(line),
                    }
                    current_content = []
                else:
                    current_content.append(line)

        # Add last section
        if current_section:
            current_section["content"] = "\n".join(current_content)
            sections.append(current_section)

    return {
        "file": filepath,
        "sections": sections,
        "pages": total_pages,
    }


def _is_heading(line: str) -> bool:
    """Detect if line is a heading."""
    line = line.strip()
    if not line:
        return False

    # Numbered headings: 1., 1.1, etc.
    if re.match(r"^\d+\.?\s+\w", line):
        return True

    # Short lines that are likely headings
    if len(line) < 80 and line.isupper():
        return True

    # Common heading patterns
    heading_patterns = [
        r"^Chapter\s+\d+",
        r"^Section\s+\d+",
        r"^Abstract",
        r"^Introduction",
        r"^Methods",
        r"^Methodology",
        r"^Results",
        r"^Discussion",
        r"^Conclusion",
        r"^References",
        r"^Appendix",
        r"^Background",
        r"^Summary",
        r"^Overview",
        r"^Acknowledgments",
    ]
    for pattern in heading_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True

    return False


def _detect_heading_level(line: str) -> int:
    """Detect heading level (1-4)."""
    line = line.strip()

    # Numbered sections
    match = re.match(r"^(\d+(?:\.\d+)*)", line)
    if match:
        parts = match.group(1).split(".")
        return min(len(parts), 4)

    # Chapter = level 1
    if re.match(r"^Chapter\s+\d+", line, re.IGNORECASE):
        return 1

    # All caps = level 1
    if line.isupper() and len(line) < 50:
        return 1

    return 2  # Default level