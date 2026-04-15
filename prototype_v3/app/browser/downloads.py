from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Download

from app.core.errors import DownloadError


def save_download(download: Download, target_dir: Path) -> Path:
    target_path = target_dir / download.suggested_filename
    download.save_as(str(target_path))
    return target_path


def list_downloaded_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [path for path in directory.iterdir() if path.is_file()]


def ensure_download_exists(path: Path) -> None:
    if not path.exists():
        raise DownloadError(f"Expected download was not created: {path.name}")
