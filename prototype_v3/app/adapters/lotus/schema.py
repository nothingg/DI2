from __future__ import annotations

from datetime import date


def build_short_date_token(run_date: date) -> str:
    return run_date.strftime("%d%m%y")


def build_long_date_token(run_date: date) -> str:
    return run_date.strftime("%d%m%Y")


def build_summary_input_date(run_date: date) -> str:
    return f"{run_date.strftime('%b')} {run_date.day}, {run_date.year}"


def build_expected_zip_prefix(run_date: date) -> str:
    token = build_long_date_token(run_date)
    return f"TES_GHB_{token}_{token}"


def build_servu_filenames(run_date: date) -> list[str]:
    token = run_date.strftime("%Y%m%d")
    return [
        f"INDCR0000000003300000230{token}001.TXT",
        f"REDCR0000000003300000230{token}001.zip",
    ]
