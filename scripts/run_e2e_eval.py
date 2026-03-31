#!/usr/bin/env python3
"""
E2E Evaluation Script for doc-genie.
Runs comprehensive tests with real documents and generates visual report.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_e2e_evaluation():
    """Run complete E2E evaluation pipeline."""
    project_root = Path(__file__).parent.parent
    results = {
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": [],
        "summary": {},
    }

    # Test cases
    test_cases = [
        {
            "name": "Python Code Extraction",
            "file": "lib/config.py",
            "expected_boxes": 12,  # GenieConfig has ~12 methods/properties
            "type": "code",
        },
        {
            "name": "Tree-Sitter Multi-Language",
            "file": "lib/extractors/tree_sitter_extractor.py",
            "expected_boxes": 5,
            "type": "code",
        },
        {
            "name": "C Code Extraction",
            "file": "tests/fixtures/sample.c",
            "expected_boxes": 5,  # 5 functions in the C file
            "type": "code",
        },
        {
            "name": "PDF Document Extraction",
            "file": "tests/fixtures/sample.pdf",
            "expected_boxes": 3,
            "type": "document",
        },
        {
            "name": "DOCX Document Extraction",
            "file": "tests/fixtures/sample.docx",
            "expected_boxes": 3,
            "type": "document",
        },
        {
            "name": "arXiv Paper Analysis",
            "file": "tests/e2e/fixtures/paper.pdf",
            "expected_boxes": 10,
            "type": "document",
        },
    ]

    total_passed = 0
    total_tests = len(test_cases)

    for test in test_cases:
        filepath = project_root / test["file"]
        if not filepath.exists():
            print(f"Skipping {test['name']}: File not found")
            continue

        # Run extraction
        result = subprocess.run(
            ["uv", "run", "genie", "extract", str(filepath), "--output", "json"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        if result.returncode != 0:
            results["tests"].append({
                "name": test["name"],
                "file": str(test["file"]),
                "status": "error",
                "error": result.stderr,
            })
            continue

        try:
            output = json.loads(result.stdout)
            # Count boxes: functions, classes (with methods), and sections
            boxes_count = 0
            for r in output:
                boxes_count += len(r.get("functions", []))
                # Count classes and their methods
                for cls in r.get("classes", []):
                    boxes_count += 1  # The class itself
                    boxes_count += len(cls.get("methods", []))  # Methods inside class
                boxes_count += len(r.get("sections", []))

            passed = boxes_count >= test["expected_boxes"] * 0.5  # Allow 50% threshold
            if passed:
                total_passed += 1

            results["tests"].append({
                "name": test["name"],
                "file": str(test["file"]),
                "type": test["type"],
                "status": "passed" if passed else "failed",
                "boxes_found": boxes_count,
                "boxes_expected": test["expected_boxes"],
                "coverage": round(boxes_count / test["expected_boxes"] * 100, 1) if test["expected_boxes"] > 0 else 0,
            })
        except json.JSONDecodeError as e:
            results["tests"].append({
                "name": test["name"],
                "file": str(test["file"]),
                "status": "parse_error",
                "error": str(e),
            })

    results["summary"] = {
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_tests - total_passed,
        "pass_rate": round(total_passed / total_tests * 100, 1) if total_tests > 0 else 0,
    }

    return results


def generate_html_report(results: dict, output_path: Path):
    """Generate visual HTML dashboard."""
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doc-Genie E2E Evaluation Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 2rem; }}
        h1 {{ font-size: 2.5rem; color: #60a5fa; margin-bottom: 0.5rem; }}
        .timestamp {{ color: #94a3b8; }}
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; text-align: center; }}
        .card-value {{ font-size: 2.5rem; font-weight: bold; color: #60a5fa; }}
        .card-label {{ color: #94a3b8; margin-top: 0.5rem; }}
        .card.passed .card-value {{ color: #22c55e; }}
        .card.failed .card-value {{ color: #ef4444; }}
        .tests-grid {{ display: grid; gap: 1rem; }}
        .test-card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; display: grid; grid-template-columns: 1fr auto; align-items: center; }}
        .test-name {{ font-weight: 600; color: #f1f5f9; }}
        .test-file {{ color: #94a3b8; font-size: 0.875rem; margin-top: 0.25rem; }}
        .test-metrics {{ display: flex; gap: 1.5rem; align-items: center; }}
        .metric {{ text-align: center; }}
        .metric-value {{ font-weight: bold; color: #60a5fa; }}
        .metric-label {{ font-size: 0.75rem; color: #94a3b8; }}
        .status-badge {{ padding: 0.5rem 1rem; border-radius: 9999px; font-weight: 600; font-size: 0.875rem; }}
        .status-passed {{ background: #166534; color: #bbf7d0; }}
        .status-failed {{ background: #991b1b; color: #fecaca; }}
        .progress-bar {{ height: 8px; background: #334155; border-radius: 4px; overflow: hidden; margin-top: 0.5rem; }}
        .progress-fill {{ height: 100%; background: #22c55e; transition: width 0.3s; }}
        .section {{ margin-bottom: 2rem; }}
        .section-title {{ font-size: 1.25rem; color: #60a5fa; margin-bottom: 1rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Doc-Genie E2E Evaluation</h1>
            <p class="timestamp">Generated: {results["timestamp"]}</p>
        </header>

        <div class="summary-cards">
            <div class="card">
                <div class="card-value">{results["summary"]["total_tests"]}</div>
                <div class="card-label">Total Tests</div>
            </div>
            <div class="card passed">
                <div class="card-value">{results["summary"]["passed"]}</div>
                <div class="card-label">Passed</div>
            </div>
            <div class="card failed">
                <div class="card-value">{results["summary"]["failed"]}</div>
                <div class="card-label">Failed</div>
            </div>
            <div class="card">
                <div class="card-value">{results["summary"]["pass_rate"]}%</div>
                <div class="card-label">Pass Rate</div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Test Results</h2>
            <div class="tests-grid">
'''

    for test in results["tests"]:
        status_class = "status-passed" if test["status"] == "passed" else "status-failed"
        coverage = test.get("coverage", 0)
        html += f'''
                <div class="test-card">
                    <div>
                        <div class="test-name">{test["name"]}</div>
                        <div class="test-file">{test["file"]}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {min(coverage, 100)}%"></div>
                        </div>
                    </div>
                    <div class="test-metrics">
                        <div class="metric">
                            <div class="metric-value">{test.get("boxes_found", 0)}</div>
                            <div class="metric-label">Boxes Found</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{test.get("boxes_expected", 0)}</div>
                            <div class="metric-label">Expected</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{coverage}%</div>
                            <div class="metric-label">Coverage</div>
                        </div>
                        <span class="status-badge {status_class}">{test["status"].upper()}</span>
                    </div>
                </div>
'''

    html += '''
            </div>
        </div>
    </div>
</body>
</html>
'''

    output_path.write_text(html)
    print(f"HTML report generated: {output_path}")


def main():
    print("Running E2E evaluation...")
    results = run_e2e_evaluation()

    # Save JSON results
    output_dir = Path(".genie/e2e")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "e2e_results.json"
    json_path.write_text(json.dumps(results, indent=2))
    print(f"JSON results saved: {json_path}")

    # Generate HTML report
    html_path = output_dir / "e2e_report.html"
    generate_html_report(results, html_path)

    # Print summary
    print(f"\n=== E2E Evaluation Summary ===")
    print(f"Total: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Pass Rate: {results['summary']['pass_rate']}%")

    return 0 if results["summary"]["pass_rate"] >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())