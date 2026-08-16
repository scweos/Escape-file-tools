from __future__ import annotations

import hashlib
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .utils import ensure_unique_path, human_size, iter_files


def _file_hash(path: Path, chunk_size: int = 1024 * 1024) -> Optional[str]:
    """
    Compute SHA-256 of a file. Returns None on any I/O or permission error.
    """
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError, IsADirectoryError):
        return None


def find_duplicates(
    directory: Path,
    *,
    delete: bool = False,
    dry_run: bool = True,
    recursive: bool = True,
    ignore: Optional[List[str]] = None,
) -> None:
    """
    Find files with identical content under the given directory.

    Safety rules:
    - Dry-run is the default behaviour.
    - Actual deletion requires both delete=True and an explicit interactive
      confirmation.
    - The file that is kept in each group is the one with the lexicographically
      smallest path (deterministic).
    """
    if not directory.exists():
        print(f"Error: path does not exist: {directory}", file=sys.stderr)
        return
    if not directory.is_dir():
        print(f"Error: not a directory: {directory}", file=sys.stderr)
        return

    print(f"Scanning: {directory}")
    print(f"  recursive = {recursive}")
    if ignore:
        print(f"  ignore   = {ignore}")
    print()

    # Phase 1: group by size (cheap filter)
    size_map: Dict[int, List[Path]] = defaultdict(list)
    total_files = 0

    for path in iter_files(directory, recursive=recursive, ignore_patterns=ignore):
        total_files += 1
        try:
            size = path.stat().st_size
            size_map[size].append(path)
        except OSError:
            continue

    print(f"Scanned {total_files} files.")

    candidates = {
        size: paths
        for size, paths in size_map.items()
        if len(paths) > 1
    }

    if not candidates:
        print("No files with identical size found. Nothing to do.")
        return

    candidate_count = sum(len(v) for v in candidates.values())
    print(f"Found {candidate_count} files sharing size with at least one other file.")
    print("Computing content hashes...")

    # Phase 2: hash only the candidates
    hash_map: Dict[str, List[Path]] = defaultdict(list)

    for paths in candidates.values():
        for path in paths:
            digest = _file_hash(path)
            if digest is None:
                print(f"  skip (unreadable): {path}", file=sys.stderr)
                continue
            hash_map[digest].append(path)

    duplicate_groups: List[Tuple[str, List[Path]]] = [
        (digest, sorted(paths, key=lambda p: p.as_posix()))
        for digest, paths in hash_map.items()
        if len(paths) > 1
    ]

    if not duplicate_groups:
        print("No content duplicates found.")
        return

    print(f"\nFound {len(duplicate_groups)} duplicate group(s):\n")

    total_reclaimable = 0
    for index, (digest, paths) in enumerate(duplicate_groups, start=1):
        size = paths[0].stat().st_size
        reclaimable = size * (len(paths) - 1)
        total_reclaimable += reclaimable

        print(f"[Group {index}]  hash={digest[:16]}...  size={human_size(size)}  reclaimable={human_size(reclaimable)}")
        for i, p in enumerate(paths):
            marker = "KEEP" if i == 0 else "delete"
            print(f"  [{i}] ({marker}) {p}")
        print()

    print(f"Total reclaimable space: {human_size(total_reclaimable)}\n")

    if dry_run or not delete:
        print("Dry-run mode. No files were deleted.")
        print("To permanently remove duplicates, re-run with --delete")
        return

    # Destructive path – require explicit confirmation
    print("You are about to permanently delete the files marked 'delete'.")
    print("This action cannot be undone.")
    answer = input("Type 'yes' (exactly) to continue: ").strip()
    if answer != "yes":
        print("Aborted. No files were deleted.")
        return

    deleted = 0
    errors = 0

    for _, paths in duplicate_groups:
        # Keep the first (lexicographically smallest) path
        for path in paths[1:]:
            try:
                path.unlink()
                print(f"Deleted: {path}")
                deleted += 1
            except OSError as exc:
                print(f"Failed to delete {path}: {exc}", file=sys.stderr)
                errors += 1

    print()
    print(f"Deleted {deleted} file(s).")
    if errors:
        print(f"Encountered {errors} error(s) during deletion.", file=sys.stderr)
