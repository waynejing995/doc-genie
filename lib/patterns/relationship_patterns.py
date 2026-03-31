import re
from typing import Any

from lib.blackbox_model import BlackBox


class PatternDetector:
    DEPENDENCY_PATTERNS = [
        r"depends?\s+on\s+{name}",
        r"requires?\s+{name}",
        r"uses?\s+{name}",
        r"calls?\s+{name}",
        r"triggers?\s+{name}",
    ]

    def detect(self, boxes: list[BlackBox]) -> list[dict[str, Any]]:
        relationships = []

        for i, box_a in enumerate(boxes):
            for box_b in boxes[i + 1 :]:
                rels = self._check_pair(box_a, box_b)
                relationships.extend(rels)

                rels_rev = self._check_pair(box_b, box_a)
                relationships.extend(rels_rev)

        return relationships

    def _check_pair(self, box_a: BlackBox, box_b: BlackBox) -> list[dict[str, Any]]:
        rels = []

        rels.extend(self._check_io_match(box_a, box_b))
        rels.extend(self._check_text_reference(box_a, box_b))

        return rels

    def _check_io_match(self, box_a: BlackBox, box_b: BlackBox) -> list[dict[str, Any]]:
        rels = []
        outputs_a = {o.name.lower() for o in box_a.outputs}
        inputs_b = {i.name.lower() for i in box_b.inputs}

        matches = outputs_a & inputs_b
        if matches:
            rels.append(
                {
                    "source": box_a.id,
                    "target": box_b.id,
                    "type": "data_flow",
                    "confidence": 0.9,
                    "evidence": f"Output {matches} matches input",
                }
            )

        return rels

    def _check_text_reference(self, box_a: BlackBox, box_b: BlackBox) -> list[dict[str, Any]]:
        rels = []
        text = getattr(box_a, "_text", "") or ""
        name_b = box_b.name.lower()

        for pattern in self.DEPENDENCY_PATTERNS:
            regex = pattern.replace("{name}", re.escape(name_b))
            if re.search(regex, text, re.IGNORECASE):
                rels.append(
                    {
                        "source": box_a.id,
                        "target": box_b.id,
                        "type": "dependency",
                        "confidence": 0.85,
                        "evidence": f"Text mentions dependency on {box_b.name}",
                    }
                )
                break

        if name_b in text.lower():
            rels.append(
                {
                    "source": box_a.id,
                    "target": box_b.id,
                    "type": "reference",
                    "confidence": 0.7,
                    "evidence": f"Text references {box_b.name}",
                }
            )

        return rels
