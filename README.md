# Escape File Tools

Local-first, dependency-free Python CLI utilities for everyday file management.

Escape from messy folders with simple, offline tools.

## Features

- Dedup: Find (and optionally remove) duplicate files by content hash (SHA-256)
- Organize: Automatically sort files into folders by extension

## Requirements

- Python 3.8+

## Installation

git clone https://github.com/scweos/Escape-file-tools.git
cd Escape-file-tools

## Usage

Find duplicates:
python main.py dedup /path/to/folder

Find and delete duplicates (use with caution):
python main.py dedup /path/to/folder --delete

Organize files by extension (recommended to dry-run first):
python main.py organize /path/to/folder --dry-run
python main.py organize /path/to/folder

## Why this project?

Many people need simple, offline tools that don't require installing heavy packages or sending data to the cloud. This project provides small, reliable utilities that just work.

## Roadmap

- Add dry-run support for dedup
- Support ignoring certain file patterns
- Add progress indicator for large directories
- Package as a proper CLI tool

## Contributing

Issues and pull requests are welcome. Please keep changes focused.

## License

MIT
