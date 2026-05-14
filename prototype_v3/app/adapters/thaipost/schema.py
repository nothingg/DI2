from __future__ import annotations

from datetime import date


def build_date_token(run_date: date) -> str:
    return run_date.strftime("%Y%m%d")


def build_indcr_filename(run_date: date) -> str:
    return f"INDCR0000000003300000256{build_date_token(run_date)}001.TXT"


def build_redcr_filename(run_date: date, sequence: int) -> str:
    return f"REDCR0000000003300000256{build_date_token(run_date)}{sequence:03d}.zip"


def build_required_filenames(run_date: date) -> list[str]:
    return [
        build_indcr_filename(run_date),
        build_redcr_filename(run_date, 1),
        build_redcr_filename(run_date, 2),
    ]
