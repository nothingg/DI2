from __future__ import annotations

from ftplib import FTP
from pathlib import Path

from app.core.config import AppSettings
from app.core.errors import ConfigurationError, DownloadError
from app.services.file_service import ensure_dir


def _connect_ftp(settings: AppSettings, log=None) -> FTP:
    if not settings.thaipost_ftp_host or not settings.thaipost_ftp_username or not settings.thaipost_ftp_password:
        raise ConfigurationError(
            "Missing THAIPOST_FTP_HOST, THAIPOST_FTP_USERNAME, or THAIPOST_FTP_PASSWORD."
        )

    ftp = FTP()
    if log:
        log(f"Connecting to FTP server: {settings.thaipost_ftp_host}:{settings.thaipost_ftp_port}")
    ftp.connect(settings.thaipost_ftp_host, settings.thaipost_ftp_port)
    ftp.login(user=settings.thaipost_ftp_username, passwd=settings.thaipost_ftp_password)
    return ftp


def list_remote_files(settings: AppSettings, remote_dir: str, log=None) -> list[str]:
    ftp = None
    try:
        ftp = _connect_ftp(settings, log=log)
        ftp.cwd(remote_dir)
        if log:
            log(f"Listing FTP directory: {remote_dir}")
        return ftp.nlst()
    except Exception as exc:
        raise DownloadError(f"Failed to list FTP directory: {remote_dir}. Reason: {exc}") from exc
    finally:
        if ftp is not None:
            if log:
                log("Disconnecting FTP client")
            try:
                ftp.quit()
                if log:
                    log("FTP client disconnected")
            except Exception as exc:
                if log:
                    log(f"FTP client disconnect failed: {exc}")
        elif log:
            log("No FTP connection was opened")


def download_file(
    settings: AppSettings,
    remote_dir: str,
    filename: str,
    local_dir: Path,
    rename_on_conflict: bool = False,
    log=None,
) -> Path:
    ensure_dir(local_dir)
    local_path = local_dir / filename
    if rename_on_conflict:
        suffix = 1
        while local_path.exists():
            local_path = local_dir / f"{local_path.stem}_{suffix}{local_path.suffix}"
            suffix += 1

    ftp = None
    try:
        ftp = _connect_ftp(settings, log=log)
        ftp.cwd(remote_dir)
        if log:
            log(f"Downloading FTP file from {remote_dir}: {filename}")
        with local_path.open("wb") as output_file:
            ftp.retrbinary(f"RETR {filename}", output_file.write)
        return local_path
    except Exception as exc:
        raise DownloadError(f"Failed to download FTP file: {filename}. Reason: {exc}") from exc
    finally:
        if ftp is not None:
            if log:
                log("Disconnecting FTP client")
            try:
                ftp.quit()
                if log:
                    log("FTP client disconnected")
            except Exception as exc:
                if log:
                    log(f"FTP client disconnect failed: {exc}")
        elif log:
            log("No FTP connection was opened")
