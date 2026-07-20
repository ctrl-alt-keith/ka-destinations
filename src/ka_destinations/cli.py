"""Command-line interface for ka-destinations."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from ka_destinations import gdocs


def _read_utf8_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file():
        raise IsADirectoryError(path)

    return path.read_text(encoding="utf-8")


def _non_empty_value(
    parser: argparse.ArgumentParser, *, label: str, value: str | None
) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        parser.error(f"{label} must not be blank")
    return normalized


def _publication_receipt(
    *,
    bundle_path: Path,
    character_count: int,
    title: str,
    folder_id: str | None,
    dry_run: bool,
    document_url: str | None,
) -> dict[str, object]:
    return {
        "bundle_path": str(bundle_path),
        "character_count": character_count,
        "destination": "google_docs",
        "document_url": document_url,
        "dry_run": dry_run,
        "folder_id": folder_id,
        "title": title,
    }


def _print_json_receipt(receipt: dict[str, object]) -> None:
    print(json.dumps(receipt, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        prog="ka-destinations",
        description=(
            "Destination-layer CLI for publishing knowledge-adapters bundle output "
            "into downstream tools."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    publish_parser = subparsers.add_parser(
        "publish",
        help="Publish bundle output to a destination.",
        description="Publish a local bundle markdown file to Google Docs.",
    )
    publish_parser.add_argument("bundle", help="Path to the bundle file to publish.")
    publish_parser.add_argument(
        "--title",
        required=True,
        help="Google Doc title.",
    )
    publish_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the input and print what would be published without calling Google APIs.",
    )
    publish_parser.add_argument(
        "--folder-id",
        help="Optional Google Drive folder ID for the newly created Google Doc.",
    )
    publish_parser.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
        help="Output format for the publication receipt.",
    )
    publish_parser.set_defaults(command="publish")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "publish":
        args.title = _non_empty_value(parser, label="--title", value=args.title)
        args.folder_id = _non_empty_value(parser, label="--folder-id", value=args.folder_id)
        bundle_path = Path(args.bundle)
        try:
            content = _read_utf8_text(bundle_path)
        except FileNotFoundError:
            parser.error(f"input file does not exist: {bundle_path}")
        except IsADirectoryError:
            parser.error(f"input path is not a file: {bundle_path}")
        except UnicodeDecodeError:
            parser.error(f"input file is not valid UTF-8 text: {bundle_path}")

        if args.dry_run:
            receipt = _publication_receipt(
                bundle_path=bundle_path,
                character_count=len(content),
                title=args.title,
                folder_id=args.folder_id,
                dry_run=True,
                document_url=None,
            )
            if args.output_format == "json":
                _print_json_receipt(receipt)
                return 0

            message = (
                "Dry run: would publish "
                f"{bundle_path} ({len(content)} characters) to Google Docs "
                f'with title "{args.title}"'
            )
            if args.folder_id:
                message += f' in Google Drive folder "{args.folder_id}".'
            else:
                message += "."
            print(message)
            return 0

        url = gdocs.publish_markdown(
            content=content,
            title=args.title,
            folder_id=args.folder_id,
        )
        if args.output_format == "json":
            _print_json_receipt(
                _publication_receipt(
                    bundle_path=bundle_path,
                    character_count=len(content),
                    title=args.title,
                    folder_id=args.folder_id,
                    dry_run=False,
                    document_url=url,
                )
            )
            return 0

        print(url)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
