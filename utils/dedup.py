import hashlib
from pathlib import Path
from collections import defaultdict


def file_hash(path: Path, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(directory: Path, delete: bool = False):
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        return

    hashes = defaultdict(list)
    for file in directory.rglob("*"):
        if file.is_file():
            try:
                h = file_hash(file)
                hashes[h].append(file)
            except Exception as e:
                print(f"Skip {file}: {e}")

    found = False
    for h, files in hashes.items():
        if len(files) > 1:
            found = True
            print(f"\nDuplicate group (hash: {h[:12]}...):")
            for i, f in enumerate(files):
                print(f"  [{i}] {f}")
            if delete:
                for f in files[1:]:
                    print(f"  Deleting {f}")
                    f.unlink()
    if not found:
        print("No duplicates found.")
