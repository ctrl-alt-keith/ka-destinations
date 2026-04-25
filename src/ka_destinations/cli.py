"""Command-line interface for ka-destinations."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


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
        description="Placeholder publish command for future destination integrations.",
    )
    publish_parser.add_argument("bundle", help="Path to the bundle file to publish.")
    publish_parser.add_argument(
        "--title",
        help="Optional destination title override.",
    )
    publish_parser.set_defaults(command="publish")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "publish":
        title_suffix = f" (title: {args.title})" if args.title else ""
        print(f"Publish is not implemented yet for {args.bundle}{title_suffix}.")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
