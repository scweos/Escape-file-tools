from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import List, Optional

from .utils import ensure_unique_path, iter_files


def organize_by_extension(
    directory: Path,
    *,
    dry_run: bool = True,
    recursive: bool = False,
    ignore: Optional[List[str]] = None,
) -> None:
    """
    Move files into subdirectories named after their extension.

    Safety rules:
    - Dry-run is the default. No files are moved unless dry_run=False.
    - Name collisions are resolved by appending a numeric suffix.
    - Only regular files are considered.
    - The original directory structure is not preserved when recursive=True;
      files are flattened into extension folders under the root.
    """
    if not directory.exists():
        print(f"Error: path does not exist: {directory}", file=sys.stderr)
        return
    if not directory.is_dir():
        print(f"Error: not a directory: {directory}", file=sys.stderr)
        return

    print(f"Organizing: {directory}")
    print(f"  dry_run   = {dry_run}")
    print(f"  recursive = {recursive}")
    if ignore:
        print(f"  ignore    = {ignore}")
    print()

    moved = 0
    skipped = 0
    errors = 0

    for src in iter_files(directory, recursive=recursive, ignore_patterns=ignore):
        # Determine extension folder name
        ext = src.suffix.lower().lstrip(".")
        if not ext:
            ext = "no_extension"

        target_dir = directory / ext
        target_path = target_dir / src.name

        # Resolve potential name collision
        final_path = ensure_unique_path(target_path)

        if dry_run:
            rel_src = src.relative_to(directory)
            rel_dst = final_path.relative_to(directory)
            print(f"[DRY-RUN] {rel_src}  ->  {rel_dst}")
            moved += 1
            continue

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(final_path))
            print(f"Moved: {src.name}  ->  {ext}/{final_path.name}")
            moved += 1
        except OSError as exc:
            print(f"Failed to move {src}: {exc}", file=sys.stderr)
            errors += 1

    print()
    if dry_run:
        print(f"Dry-run complete. {moved} file(s) would be moved.")
        print("Re-run with --no-dry-run to apply the changes.")
    else:
        print(f"Moved {moved} file(s).")
        if errors:
            print(f"Encountered {errors} error(s).", file=sys.stderr)
