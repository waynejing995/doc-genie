#!/usr/bin/env python3
"""
Baseline comparison script for doc-genie evaluation.
Compares skill-enhanced results against baseline.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: str) -> dict:
    """Load JSON file."""
    return json.loads(Path(path).read_text())


def compare_baselines(
    baseline_path: str = ".genie/baseline.json",
    skill_result_path: str = ".genie/boxes.json",
    output_path: str = ".genie/comparison.json",
) -> dict:
    """
    Compare skill-enhanced results against baseline.

    Args:
        baseline_path: Path to baseline results
        skill_result_path: Path to skill-enhanced results
        output_path: Where to save comparison report

    Returns:
        Comparison report dict
    """
    baseline_file = Path(baseline_path)
    skill_file = Path(skill_result_path)

    comparison = {
        "version": "1.0",
        "compared_at": datetime.now(timezone.utc).isoformat(),
        "baseline_source": str(baseline_path),
        "skill_source": str(skill_result_path),
        "metrics": {},
        "improvements": [],
        "regressions": [],
        "summary": {},
    }

    # Load baseline
    if baseline_file.exists():
        baseline = load_json(baseline_path)
        baseline_boxes = baseline.get("statistics", {}).get("total_boxes", 0)
        baseline_files = baseline.get("statistics", {}).get("total_files", 0)
    else:
        print(f"Warning: Baseline not found at {baseline_path}", file=sys.stderr)
        baseline = {}
        baseline_boxes = 0
        baseline_files = 0

    # Load skill results
    if skill_file.exists():
        skill_result = load_json(skill_file_path)
        skill_boxes = skill_result.get("boxes", [])
        skill_count = len(skill_boxes)
    else:
        print(f"Warning: Skill results not found at {skill_result_path}", file=sys.stderr)
        skill_result = {}
        skill_count = 0

    # Calculate metrics
    comparison["metrics"] = {
        "baseline_boxes": baseline_boxes,
        "skill_boxes": skill_count,
        "difference": skill_count - baseline_boxes,
        "percentage_change": (
            ((skill_count - baseline_boxes) / baseline_boxes * 100)
            if baseline_boxes > 0
            else 0
        ),
    }

    # Compare by type
    if baseline.get("statistics", {}).get("by_type"):
        comparison["metrics"]["baseline_by_type"] = baseline["statistics"]["by_type"]

    # Quality checks (if skill results have confidence/quality scores)
    if skill_count > 0:
        # Check for structured output
        structured_count = sum(
            1 for b in skill_boxes
            if isinstance(b, dict) and "id" in b and "name" in b
        )
        comparison["metrics"]["structured_boxes"] = structured_count
        comparison["metrics"]["structured_percentage"] = (
            structured_count / skill_count * 100 if skill_count > 0 else 0
        )

    # Generate summary
    comparison["summary"] = {
        "baseline_exists": baseline_file.exists(),
        "skill_result_exists": skill_file.exists(),
        "total_files_processed": baseline_files,
        "extraction_coverage": f"{comparison['metrics']['percentage_change']:.1f}%",
        "structured_output": f"{comparison['metrics'].get('structured_percentage', 0):.1f}%",
    }

    # Save comparison
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(comparison, indent=2, ensure_ascii=False))

    print(f"Comparison saved to {output_path}")
    print(f"Baseline boxes: {baseline_boxes}")
    print(f"Skill boxes: {skill_count}")
    print(f"Difference: {comparison['metrics']['difference']} ({comparison['metrics']['percentage_change']:.1f}%)")

    return comparison


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compare baseline vs skill results")
    parser.add_argument("--baseline", "-b", default=".genie/baseline.json")
    parser.add_argument("--skill", "-s", default=".genie/boxes.json")
    parser.add_argument("--output", "-o", default=".genie/comparison.json")

    args = parser.parse_args()
    compare_baselines(args.baseline, args.skill, args.output)


if __name__ == "__main__":
    main()