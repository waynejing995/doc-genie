import argparse
import sys


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="genie", description="doc-genie: Document analysis tool")
    subparsers = parser.add_subparsers(dest="command")

    extract_parser = subparsers.add_parser("extract", help="Extract black boxes from files")
    extract_parser.add_argument("files", nargs="+", help="Files to analyze")

    subparsers.add_parser("analyze", help="Analyze relationships")

    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.add_argument("--format", default="markdown", choices=["markdown", "html", "dot"])

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.command == "extract":
        from lib.extractors.code_analyzer import CodeAnalyzer
        from lib.extractors.markdown_extractor import MarkdownExtractor

        for filepath in args.files:
            if filepath.endswith(".md"):
                extractor = MarkdownExtractor()
            else:
                extractor = CodeAnalyzer()
            result = extractor.extract_from_file(filepath)
            print(
                f"Extracted from {filepath}: {len(result.get('sections', result.get('functions', [])))} items"
            )

    elif args.command == "analyze":
        print("Analyzing relationships...")

    elif args.command == "report":
        print(f"Generating {args.format} report...")

    else:
        print("Usage: genie [extract|analyze|report]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
