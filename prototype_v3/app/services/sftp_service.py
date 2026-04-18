from __future__ import annotations

from pathlib import Path

import paramiko

from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError
from app.services.file_service import ensure_dir


def download_file(
    settings: AppSettings,
    remote_dir: str,
    filename: str,
    local_dir: Path,
    rename_on_conflict: bool = False,
) -> Path:
    if not settings.servu_host or not settings.servu_username or not settings.servu_password:
        raise ConfigurationError("Missing SERVU_HOST, SERVU_USERNAME, or SERVU_PASSWORD.")

    ensure_dir(local_dir)
    local_path = local_dir / filename
    if rename_on_conflict:
        suffix = 1
        while local_path.exists():
            local_path = local_dir / f"{local_path.stem}_{suffix}{local_path.suffix}"
            suffix += 1
    transport = None
    sftp = None

    try:
        transport = paramiko.Transport((settings.servu_host, settings.servu_port))
        transport.connect(username=settings.servu_username, password=settings.servu_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.chdir(remote_dir)
        sftp.get(f"{remote_dir}{filename}", str(local_path))
        return local_path
    except Exception as exc:
        raise DownloadError(f"Failed to download SFTP file: {filename}") from exc
    finally:
        if sftp is not None:
            sftp.close()
        if transport is not None:
            transport.close()
