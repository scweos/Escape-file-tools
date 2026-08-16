from pathlib import Path
import shutil


def organize_by_extension(directory: Path, dry_run: bool = False):
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        return

    for file in directory.iterdir():
        if file.is_file():
            ext = file.suffix.lower().lstrip(".") or "no_extension"
            target_dir = directory / ext
            target_path = target_dir / file.name

            if dry_run:
                print(f"[DRY-RUN] Would move {file.name} → {ext}/")
            else:
                target_dir.mkdir(exist_ok=True)
                shutil.move(str(file), str(target_path))
                print(f"Moved {file.name} → {ext}/")
