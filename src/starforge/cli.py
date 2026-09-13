from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .audit import audit_repo, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="starforge",
        description="Audit a repository for GitHub star-readiness signals.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to audit. Defaults to the current directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.path)

    if not root.exists():
        print(f"starforge: path does not exist: {root}", file=sys.stderr)
        return 2

    audit = audit_repo(root)
    if args.json:
        print(json.dumps(audit.to_dict(), indent=2))
    else:
        print(render_text(audit), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
