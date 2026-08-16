#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .dedup import find_duplicates
from .organize import organize_by_extension
from .rename import batch_rename


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="escape-files",
        description="Local-first file utilities: deduplication, organization and batch renaming.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  escape-files dedup ~/Downloads
  escape-files dedup ~/Downloads --delete
  escape-files organize ~/Desktop
  escape-files organize ~/Desktop --no-dry-run
  escape-files rename ./photos --prefix img_ --start 1
  escape-files rename ./photos --prefix img_ --start 1 --no-dry-run
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---------- dedup ----------
    p_dedup = subparsers.add_parser(
        "dedup",
        help="Find and optionally remove duplicate files by content hash",
    )
    p_dedup.add_argument(
        "path",
        type=str,
        help="Target directory",
    )
    p_dedup.add_argument(
        "--delete",
        action="store_true",
        help="Permanently delete duplicate files (requires interactive confirmation)",
    )
    p_dedup.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not scan subdirectories",
    )
    p_dedup.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        metavar="PATTERN",
        help="Glob patterns to ignore (matched against relative path and filename)",
    )

    # ---------- organize ----------
    p_org = subparsers.add_parser(
        "organize",
        help="Move files into folders named by their extension",
    )
    p_org.add_argument(
        "path",
        type=str,
        help="Target directory",
    )
    p_org.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually move files (default is dry-run)",
    )
    p_org.add_argument(
        "--recursive",
        action="store_true",
        help="Also process files in subdirectories (files will be flattened)",
    )
    p_org.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        metavar="PATTERN",
        help="Glob patterns to ignore",
    )

    # ---------- rename ----------
    p_rename = subparsers.add_parser(
        "rename",
        help="Batch rename files with prefix, suffix, numbering and optional date",
    )
    p_rename.add_argument(
        "path",
        type=str,
        help="Target directory",
    )
    p_rename.add_argument(
        "--prefix",
        default="",
        help="String prepended to the new filename",
    )
    p_rename.add_argument(
        "--suffix",
        default="",
        help="String appended before the extension",
    )
    p_rename.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting number for sequential naming (default: 1)",
    )
    p_rename.add_argument(
        "--date",
        action="store_true",
        help="Prepend current date (YYYYMMDD) to the filename",
    )
    p_rename.add_argument(
        "--pattern",
        default=None,
        help="Simple string replacement in the form old=new",
    )
    p_rename.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually rename files (default is dry-run)",
    )
    p_rename.add_argument(
        "--recursive",
        action="store_true",
        help="Also process files in subdirectories",
    )
    p_rename.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        metavar="PATTERN",
        help="Glob patterns to ignore",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    path = Path(args.path).expanduser().resolve()

    if args.command == "dedup":
        find_duplicates(
            path,
            delete=args.delete,
            dry_run=not args.delete,
            recursive=not args.no_recursive,
            ignore=args.ignore or None,
        )
        return 0

    if args.command == "organize":
        organize_by_extension(
            path,
            dry_run=not args.no_dry_run,
            recursive=args.recursive,
            ignore=args.ignore or None,
        )
        return 0

    if args.command == "rename":
        batch_rename(
            path,
            prefix=args.prefix,
            suffix=args.suffix,
            start_number=args.start,
            use_date=args.date,
            pattern=args.pattern,
            dry_run=not args.no_dry_run,
            recursive=args.recursive,
            ignore=args.ignore or None,
        )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
