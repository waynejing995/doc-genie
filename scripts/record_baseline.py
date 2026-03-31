#!/usr/bin/env python3
"""
Baseline recording script for doc-genie evaluation.
Records extraction results without skill intervention for comparison.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def record_baseline(
    input_files: list[str],
    output_path: str = ".genie/baseline.json",
    depth: str = "medium",
) -> dict:
    """
    Record baseline extraction results without skill processing.

    Args:
        input_files: List of files to extract from
        output_path: Where to save baseline results
        depth: Extraction depth profile

    Returns:
        Baseline results dict
    """
    from lib.config import GenieConfig
    from lib.extractors.tree_sitter_extractor import extract_structure
    from lib.extractors.pdf_extractor import extract_from_pdf
    from lib.extractors.docx_extractor import extract_from_docx
    from lib.extractors.markdown_extractor import MarkdownExtractor

    config = GenieConfig()
    results = {
        "version": "1.0",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "depth": depth,
        "files": [],
        "statistics": {
            "total_files": len(input_files),
            "total_boxes": 0,
            "by_type": {},
            "by_file_type": {},
        },
    }

    for filepath in input_files:
        path = Path(filepath)
        if not path.exists():
            print(f"Warning: File not found: {filepath}", file=sys.stderr)
            continue

        suffix = path.suffix.lower()

        try:
            if suffix == ".md":
                extractor = MarkdownExtractor()
                file_result = extractor.extract_from_file(filepath)
                boxes = file_result.get("sections", [])
            elif suffix == ".pdf":
                file_result = extract_from_pdf(filepath)
                boxes = file_result.get("sections", [])
            elif suffix in (".docx", ".doc"):
                file_result = extract_from_docx(filepath)
                boxes = file_result.get("sections", [])
            else:
                file_result = extract_structure(filepath)
                boxes = file_result.get("functions", []) + file_result.get("classes", [])

            file_record = {
                "path": filepath,
                "type": suffix,
                "boxes_count": len(boxes),
                "boxes": boxes[:10],  # Store first 10 as sample
            }
            results["files"].append(file_record)
            results["statistics"]["total_boxes"] += len(boxes)

            # Count by file type
            if suffix not in results["statistics"]["by_file_type"]:
                results["statistics"]["by_file_type"][suffix] = 0
            results["statistics"]["by_file_type"][suffix] += len(boxes)

            # Count by box type
            for box in boxes:
                box_type = box.get("type", "unknown")
                if box_type not in results["statistics"]["by_type"]:
                    results["statistics"]["by_type"][box_type] = 0
                results["statistics"]["by_type"][box_type] += 1

        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
            results["files"].append({
                "path": filepath,
                "error": str(e),
            })

    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))

    print(f"Baseline recorded to {output_path}")
    print(f"Total files: {results['statistics']['total_files']}")
    print(f"Total boxes: {results['statistics']['total_boxes']}")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Record baseline extraction results")
    parser.add_argument("files", nargs="+", help="Files to extract from")
    parser.add_argument("--output", "-o", default=".genie/baseline.json", help="Output path")
    parser.add_argument("--depth", "-d", default="medium", choices=["quick", "medium", "deep"])

    args = parser.parse_args()
    record_baseline(args.files, args.output, args.depth)


if __name__ == "__main__":
    main()