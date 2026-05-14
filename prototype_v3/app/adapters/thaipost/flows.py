from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.adapters.thaipost import locators, schema
from app.core.config import AppSettings
from app.core.errors import NoDataError, PartialDataError, ValidationError
from app.services.file_service import list_files
from app.services.ftp_service import download_file as download_ftp_file
from app.services.ftp_service import list_remote_files


@dataclass(slots=True)
class ThaiPostAvailability:
    required_available: list[str]
    required_missing: list[str]


@dataclass(slots=True)
class ThaiPostDownloadResult:
    availability: ThaiPostAvailability
    downloaded_files: list[Path]


def inspect_ftp_availability(settings: AppSettings, run_date: date, log) -> ThaiPostAvailability:
    remote_names = {name.lower() for name in list_remote_files(settings, settings.thaipost_ftp_path, log=log)}
    required_available: list[str] = []
    required_missing: list[str] = []

    for file_name in schema.build_required_filenames(run_date):
        if file_name.lower() in remote_names:
            required_available.append(file_name)
        else:
            required_missing.append(file_name)

    return ThaiPostAvailability(
        required_available=required_available,
        required_missing=required_missing,
    )


def build_no_data_message(run_date: date) -> str:
    return (
        f"No {locators.FTP_SOURCE_LABEL} data was found for run date {run_date.isoformat()}. "
        "This usually means the selected date is wrong or the source has not published data yet."
    )


def build_partial_data_message(run_date: date, availability: ThaiPostAvailability) -> str:
    return (
        "Thai Post returned partial data for "
        f"run date {run_date.isoformat()}. "
        f"Available: {', '.join(availability.required_available)}. "
        f"Missing required files: {', '.join(availability.required_missing)}."
    )


def download_ftp_reports(
    settings: AppSettings,
    run_date: date,
    temp_dir: Path,
    log,
) -> ThaiPostDownloadResult:
    availability = inspect_ftp_availability(settings, run_date, log)
    if not availability.required_available:
        raise NoDataError(build_no_data_message(run_date))

    downloaded_files: list[Path] = []
    for file_name in availability.required_available:
        log(f"Downloading Thai Post FTP file: {file_name}")
        downloaded_files.append(
            download_ftp_file(
                settings=settings,
                remote_dir=settings.thaipost_ftp_path,
                filename=file_name,
                local_dir=temp_dir,
                log=log,
            )
        )

    return ThaiPostDownloadResult(
        availability=availability,
        downloaded_files=downloaded_files,
    )


def validate_downloads(temp_dir: Path, run_date: date, include_servu: bool) -> None:
    files = {path.name for path in list_files(temp_dir)}
    missing: list[str] = []

    for file_name in schema.build_required_filenames(run_date):
        if include_servu:
            stem = Path(file_name).stem
            suffix = Path(file_name).suffix
            matching = [
                name for name in files
                if name == file_name or (name.startswith(f"{stem}_") and name.endswith(suffix))
            ]
            if len(matching) < 2:
                missing.append(file_name)
        elif file_name not in files:
            missing.append(file_name)

    if missing:
        if files:
            raise PartialDataError(
                "Thai Post workflow returned partial data. "
                f"Missing expected downloaded files: {', '.join(sorted(missing))}"
            )
        raise ValidationError(f"Missing expected downloaded files: {', '.join(sorted(missing))}")
