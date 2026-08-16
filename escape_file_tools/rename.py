from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .utils import ensure_unique_path, iter_files


def batch_rename(
    directory: Path,
    *,
    prefix: str = "",
    suffix: str = "",
    start_number: int = 1,
    use_date: bool = False,
    pattern: Optional[str] = None,
    dry_run: bool = True,
    recursive: bool = False,
    ignore: Optional[List[str]] = None,
) -> None:
    """
    Batch rename files under the given directory.

    Naming rules (applied in order):
    1. Optional date prefix (YYYYMMDD_)
    2. User-supplied prefix
    3. Zero-padded sequential number (starting from start_number)
    4. User-supplied suffix
    5. Original file extension is always preserved
    6. Optional simple string replacement via pattern="old=new"

    Safety rules:
    - Dry-run is the default.
    - Name collisions are automatically resolved with a numeric suffix.
    - Only regular files are processed.
    """
    if not directory.exists():
        print(f"Error: path does not exist: {directory}", file=sys.stderr)
        return
    if not directory.is_dir():
        print(f"Error: not a directory: {directory}", file=sys.stderr)
        return

    if start_number < 0:
        print("Error: start_number must be >= 0", file=sys.stderr)
        return

    print(f"Renaming files in: {directory}")
    print(f"  dry_run      = {dry_run}")
    print(f"  recursive    = {recursive}")
    print(f"  prefix       = {prefix!r}")
    print(f"  suffix       = {suffix!r}")
    print(f"  start_number = {start_number}")
    print(f"  use_date     = {use_date}")
    if pattern:
        print(f"  pattern      = {pattern!r}")
    if ignore:
        print(f"  ignore       = {ignore}")
    print()

    files = sorted(
        iter_files(directory, recursive=recursive, ignore_patterns=ignore),
        key=lambda p: p.as_posix(),
    )

    if not files:
        print("No files found to rename.")
        return

    print(f"Found {len(files)} file(s).\n")

    renamed = 0
    errors = 0
    date_str = datetime.now().strftime("%Y%m%d") if use_date else ""

    for index, src in enumerate(files):
        original_name = src.name
        ext = src.suffix

        # Build new stem
        number = start_number + index
        new_stem = f"{prefix}{number:04d}{suffix}"

        if use_date:
            new_stem = f"{date_str}_{new_stem}"

        if pattern and "=" in pattern:
            old, new = pattern.split("=", 1)
            new_stem = new_stem.replace(old, new)

        new_name = new_stem + ext
        target = src.with_name(new_name)

        # Ensure uniqueness inside the same directory
        final_path = ensure_unique_path(target)

        if dry_run:
            print(f"[DRY-RUN] {original_name}  ->  {final_path.name}")
            renamed += 1
            continue

        try:
            src.rename(final_path)
            print(f"Renamed: {original_name}  ->  {final_path.name}")
            renamed += 1
        except OSError as exc:
            print(f"Failed to rename {src}: {exc}", file=sys.stderr)
            errors += 1

    print()
    if dry_run:
        print(f"Dry-run complete. {renamed} file(s) would be renamed.")
        print("Re-run with --no-dry-run to apply the changes.")
    else:
        print(f"Renamed {renamed} file(s).")
        if errors:
            print(f"Encountered {errors} error(s).", file=sys.stderr)
