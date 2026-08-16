# Escape File Tools

Local-first, zero-dependency command-line utilities for everyday file management.

Escape File Tools is a small, focused set of Python utilities designed to help you clean up and reorganize files on your local machine without relying on any external services or heavy dependencies. It prioritizes safety, predictability, and simplicity.

The tool provides three core commands:

- Deduplication of files by content
- Organization of files by file extension
- Batch renaming with flexible naming rules

All operations are performed entirely offline. No data is uploaded, no network requests are made, and no telemetry is collected.

## Design Goals

- **Safe by default**: Destructive operations require explicit flags. Deletion of duplicates additionally requires interactive confirmation.
- **Deterministic behavior**: When multiple files have identical content, the file with the lexicographically smallest path is kept. This makes results reproducible.
- **Minimal dependencies**: Only the Python standard library is used. There are no third-party packages required at runtime.
- **Predictable dry-run**: Most operations default to dry-run mode so you can review the planned changes before applying them.
- **Clear feedback**: The tool prints structured information about what it finds and what it intends to do.

## Features

### Dedup

Scans a directory for files that have identical content using SHA-256 hashing.

- First groups files by size (cheap filter)
- Only computes cryptographic hashes for files that share the same size
- Supports recursive and non-recursive scanning
- Supports ignore patterns
- Dry-run by default
- Actual deletion requires the `--delete` flag and typing `yes` at the confirmation prompt
- The kept file in each duplicate group is chosen deterministically

### Organize

Moves files into subdirectories named after their file extension.

- Files without an extension are placed into a folder named `no_extension`
- Name collisions are automatically resolved by appending a numeric suffix
- Supports recursive mode (files are flattened into extension folders under the root)
- Dry-run by default
- Supports ignore patterns

### Rename

Batch renames files according to a consistent naming scheme.

- Supports prefix and suffix
- Supports sequential numbering with zero-padding
- Supports optional date prefix (`YYYYMMDD_`)
- Supports simple string replacement via `--pattern old=new`
- Original file extension is always preserved
- Name collisions are automatically resolved
- Dry-run by default
- Supports recursive mode and ignore patterns

## Requirements

- Python 3.8 or later
- No third-party packages required

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/scweos/Escape-file-tools.git
cd Escape-file-tools
pip install -e .
```

After installation the `escape-files` command is available in your environment:

```bash
escape-files --help
```

You can also run the module directly without installing:

```bash
python -m escape_file_tools.cli --help
```

## Usage

### Find duplicate files

Preview mode (recommended first step):

```bash
escape-files dedup /path/to/folder
```

Actually delete duplicates (will ask for confirmation):

```bash
escape-files dedup /path/to/folder --delete
```

Do not scan subdirectories:

```bash
escape-files dedup /path/to/folder --no-recursive
```

Ignore certain patterns:

```bash
escape-files dedup /path/to/folder --ignore "*.tmp" ".DS_Store" "Thumbs.db"
```

### Organize files by extension

Preview:

```bash
escape-files organize /path/to/folder
```

Apply the changes:

```bash
escape-files organize /path/to/folder --no-dry-run
```

Process files in subdirectories as well:

```bash
escape-files organize /path/to/folder --recursive --no-dry-run
```

### Batch rename files

Preview a sequential rename:

```bash
escape-files rename /path/to/folder --prefix img_ --start 1
```

Apply the rename:

```bash
escape-files rename /path/to/folder --prefix img_ --start 1 --no-dry-run
```

Add a date prefix:

```bash
escape-files rename /path/to/folder --prefix photo_ --date --no-dry-run
```

Simple string replacement:

```bash
escape-files rename /path/to/folder --pattern "oldname=newname" --no-dry-run
```

Combine options:

```bash
escape-files rename /path/to/folder --prefix trip_ --suffix _final --start 100 --date --no-dry-run
```

## Safety Notes

- Always run commands in dry-run / preview mode first.
- The `--delete` flag for deduplication is irreversible once confirmed. Make sure you have backups of important data.
- When using `--recursive` with organize, files from subdirectories are flattened into extension folders at the root level. The original subdirectory structure is not preserved.
- The tool only operates on regular files. Symbolic links, directories, and special files are skipped.

## Project Structure

```text
escape_file_tools/
├── __init__.py
├── cli.py          # Command-line interface
├── dedup.py        # Duplicate detection and removal
├── organize.py     # Extension-based organization
├── rename.py       # Batch renaming
└── utils.py        # Shared helpers
```

## License

MIT License. See the LICENSE file for details.
