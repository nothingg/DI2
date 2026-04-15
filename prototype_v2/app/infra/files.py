from __future__ import annotations

import shutil
from pathlib import Path

from app.core.errors import ValidationError
from app.core.models import DownloadArtifact


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_files(path: Path) -> list[Path]:
    return [item for item in path.iterdir() if item.is_file()]


def move_to_output(temp_dir: Path, output_dir: Path) -> list[DownloadArtifact]:
    ensure_dir(output_dir)
    artifacts: list[DownloadArtifact] = []
    for source in list_files(temp_dir):
        target = output_dir / source.name
        shutil.move(str(source), str(target))
        artifacts.append(DownloadArtifact(name=target.name, path=target))
    return artifacts


def require_files(files: list[Path]) -> None:
    if not files:
        raise ValidationError("No files were downloaded into the temp directory.")
