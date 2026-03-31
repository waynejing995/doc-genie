"""doc-genie CLI - unified command line interface."""

import argparse
import json
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="genie", description="doc-genie: Document analysis tool"
    )
    subparsers = parser.add_subparsers(dest="command")

    # extract command
    ext = subparsers.add_parser("extract", help="Extract black boxes from files")
    ext.add_argument("files", nargs="+", help="Files to analyze")
    ext.add_argument(
        "--output", "-o", default="text", choices=["text", "json"], help="Output format"
    )
    ext.add_argument("--depth", "-d", choices=["quick", "medium", "deep"], help="Extraction depth")

    # init command
    subparsers.add_parser("init", help="Initialize .genie directory")

    # config command
    cfg = subparsers.add_parser("config", help="Show configuration")
    cfg.add_argument("action", choices=["show", "set"])

    # analyze command
    subparsers.add_parser("analyze", help="Analyze relationships")

    # report command
    rpt = subparsers.add_parser("report", help="Generate report")
    rpt.add_argument("--format", "-f", default="markdown", choices=["markdown", "html", "dot"])
    rpt.add_argument("--output", "-o", help="Output file path")

    return parser.parse_args(argv)


def extract(files: list[str], output: str = "text", depth: str | None = None) -> list[dict]:
    """Extract structure from files."""
    from lib.config import GenieConfig

    config = GenieConfig()
    depth = depth or config.depth

    results = []
    for filepath in files:
        path = Path(filepath)
        suffix = path.suffix.lower()

        if suffix == ".md":
            from lib.extractors.markdown_extractor import MarkdownExtractor

            extractor = MarkdownExtractor()
            result = extractor.extract_from_file(filepath)
        elif suffix == ".pdf":
            from lib.extractors.pdf_extractor import extract_from_pdf

            result = extract_from_pdf(filepath)
        elif suffix in (".docx", ".doc"):
            from lib.extractors.docx_extractor import extract_from_docx

            result = extract_from_docx(filepath)
        else:
            from lib.extractors.tree_sitter_extractor import extract_structure

            result = extract_structure(filepath)

        result["_depth"] = depth
        results.append(result)

    if output == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            count = len(r.get("sections", r.get("functions", [])))
            print(f"Extracted from {r['file']}: {count} items (depth={depth})")

    return results


def init_genie():
    """Initialize .genie directory with default config."""
    from lib.config import DEFAULT_CONFIG
    import yaml

    genie_dir = Path(".genie")
    genie_dir.mkdir(exist_ok=True)

    config_file = genie_dir / "config.yaml"
    if config_file.exists():
        print("Config already exists at .genie/config.yaml")
        return

    config_file.write_text(yaml.dump(DEFAULT_CONFIG, default_flow_style=False))
    print("Created .genie/config.yaml with default configuration")


def show_config():
    """Show current configuration."""
    from lib.config import GenieConfig
    import yaml

    config = GenieConfig()
    print(yaml.dump(config._config, default_flow_style=False))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.command == "extract":
        extract(args.files, args.output, args.depth)
    elif args.command == "init":
        init_genie()
    elif args.command == "config":
        if args.action == "show":
            show_config()
    elif args.command == "analyze":
        print("Analyzing relationships...")
        # TODO: Implement analyze
    elif args.command == "report":
        print(f"Generating {args.format} report...")
        # TODO: Implement report
    else:
        print("Usage: genie [extract|init|config|analyze|report]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())