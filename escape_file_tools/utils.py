from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional
import fnmatch
import os


def iter_files(
    directory: Path,
    recursive: bool = True,
    ignore_patterns: Optional[List[str]] = None,
) -> Iterable[Path]:
    """
    Yield files under the given directory with optional ignore patterns.

    Args:
        directory: Root directory to scan.
        recursive: If True, walk subdirectories.
        ignore_patterns: List of glob patterns to skip (matched against
                         relative path and basename).

    Yields:
        Path objects for regular files only.
    """
    if not directory.is_dir():
        return

    ignore_patterns = ignore_patterns or []

    if recursive:
        walker = directory.rglob("*")
    else:
        walker = directory.iterdir()

    for path in walker:
        try:
            if not path.is_file():
                continue
        except OSError:
            continue

        try:
            rel = path.relative_to(directory).as_posix()
        except ValueError:
            continue

        name = path.name

        skipped = False
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(name, pattern):
                skipped = True
                break
        if skipped:
            continue

        yield path


def human_size(num_bytes: int) -> str:
    """
    Convert a byte count into a human-readable string.
    """
    if num_bytes < 0:
        return "0B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)}{unit}"
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


def ensure_unique_path(target: Path) -> Path:
    """
    If the target path already exists, append a numeric suffix until unique.
    """
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
