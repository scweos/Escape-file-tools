#!/usr/bin/env python3
"""
Escape File Tools - Local-first file utilities
"""

import argparse
from pathlib import Path
from utils.dedup import find_duplicates
from utils.organize import organize_by_extension


def main():
    parser = argparse.ArgumentParser(description="Escape File Tools - Simple local file utilities")
    subparsers = parser.add_subparsers(dest="command")

    # dedup 命令
    dedup_parser = subparsers.add_parser("dedup", help="Find duplicate files by content hash")
    dedup_parser.add_argument("path", type=str, help="Directory to scan")
    dedup_parser.add_argument("--delete", action="store_true", help="Actually delete duplicates (use with caution)")

    # organize 命令
    org_parser = subparsers.add_parser("organize", help="Organize files by extension")
    org_parser.add_argument("path", type=str, help="Directory to organize")
    org_parser.add_argument("--dry-run", action="store_true", help="Only show what would be done")

    args = parser.parse_args()

    if args.command == "dedup":
        find_duplicates(Path(args.path), delete=args.delete)
    elif args.command == "organize":
        organize_by_extension(Path(args.path), dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
