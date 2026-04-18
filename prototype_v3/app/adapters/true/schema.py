from __future__ import annotations

from datetime import date


def build_date_token(run_date: date) -> str:
    return run_date.strftime("%Y%m%d")


def build_calendar_title(run_date: date) -> str:
    return run_date.strftime(f"%B {run_date.day}, %Y")


def build_web_filenames(run_date: date) -> list[str]:
    token = build_date_token(run_date)
    return [
        f"TRUE{token}01.txt",
        f"TMNGHBRPTEW_C101{token}.pdf",
        f"TMNGHBRPTEW_C102{token}.pdf",
        f"TMNGHBRPTTRM_C101{token}.pdf",
        f"TMNGHBRPTTRM_C102{token}.pdf",
    ]


def build_servu_filenames(run_date: date) -> list[str]:
    token = build_date_token(run_date)
    return [
        f"INDCR0000000003300000248{token}001.TXT",
        f"REDCR0000000003300000248{token}001.zip",
    ]
