from __future__ import annotations

from pathlib import Path

from app.core.errors import ValidationError
from app.core.models import OutputFile


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return [item for item in path.iterdir() if item.is_file()]


def require_files(files: list[Path]) -> None:
    if not files:
        raise ValidationError("No downloaded files were found in the temp directory.")


def move_to_output(temp_dir: Path, output_dir: Path) -> list[OutputFile]:
    ensure_dir(output_dir)
    moved_files: list[OutputFile] = []
    for file_path in list_files(temp_dir):
        destination = output_dir / file_path.name
        file_path.replace(destination)
        moved_files.append(OutputFile(path=destination, name=destination.name))
    return moved_files
