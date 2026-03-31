import re
from pathlib import Path
from typing import Any


class MarkdownExtractor:
    SECTION_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    INPUT_PATTERN = re.compile(r"(?:input|parameter|argument)s?:\s*(.+)", re.IGNORECASE)
    OUTPUT_PATTERN = re.compile(r"(?:output|result|return)s?:\s*(.+)", re.IGNORECASE)

    def extract_sections(self, content: str) -> list[dict[str, Any]]:
        sections = []
        matches = list(self.SECTION_PATTERN.finditer(content))

        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start:end].strip()

            sections.append(
                {
                    "level": level,
                    "title": title,
                    "content": section_content,
                    "line": content[: match.start()].count("\n") + 1,
                }
            )

        return sections

    def extract_io(self, content: str) -> dict[str, list[str]]:
        inputs = []
        outputs = []

        input_match = self.INPUT_PATTERN.search(content)
        if input_match:
            start = input_match.start()
            next_section = re.search(
                r"\n(?:output|return|constraint|note)s?:", content[start:], re.IGNORECASE
            )
            end = start + next_section.start() if next_section else len(content)
            block = content[start:end]
            inputs = re.findall(r"^[\s*-]+(.+)$", block, re.MULTILINE)
            inputs = [i.strip() for i in inputs if i.strip()]

        output_match = self.OUTPUT_PATTERN.search(content)
        if output_match:
            start = output_match.start()
            next_section = re.search(
                r"\n(?:input|constraint|note)s?:", content[start:], re.IGNORECASE
            )
            end = start + next_section.start() if next_section else len(content)
            block = content[start:end]
            outputs = re.findall(r"^[\s*-]+(.+)$", block, re.MULTILINE)
            outputs = [o.strip() for o in outputs if o.strip()]

        return {"inputs": inputs, "outputs": outputs}

    def extract_from_file(self, filepath: str) -> dict[str, Any]:
        content = Path(filepath).read_text()
        sections = self.extract_sections(content)

        for section in sections:
            section["io"] = self.extract_io(section["content"])

        return {"file": filepath, "sections": sections}
