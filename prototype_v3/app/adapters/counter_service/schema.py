from __future__ import annotations

from datetime import date, timedelta
from urllib.parse import quote


def build_date_token(run_date: date) -> str:
    return run_date.strftime("%Y%m%d")


def build_next_day_mmdd(run_date: date) -> str:
    return (run_date + timedelta(days=1)).strftime("%m%d")


def build_report_token(run_date: date) -> str:
    return run_date.strftime("%d%m%y")


def build_daily_zip_filename(run_date: date) -> str:
    return f"261{build_next_day_mmdd(run_date)}.zip"


def build_indcr_filename(run_date: date) -> str:
    return f"INDCR0000000003300000264{build_date_token(run_date)}001.txt"


def build_gco_filename(run_date: date) -> str:
    return f"gco261{build_next_day_mmdd(run_date)}.zip"


def build_report_zip_filename(run_date: date) -> str:
    return f"Report_GHB_{build_report_token(run_date)}.zip"


def _encode_ticketnet_filename(filename: str) -> str:
    encoded = quote(filename, safe="")
    return encoded.replace(".", "%2E")


def build_ticketnet_href(filename: str) -> str:
    return f"downloadclientfile.asp?file=GHB\\{_encode_ticketnet_filename(filename)}"


def build_download_fragments(filename: str) -> list[str]:
    fragments = ["downloadclientfile.asp"]
    stem = filename.rsplit(".", 1)[0]

    if filename.startswith("Report_GHB_"):
        report_token = stem.split("_")[-1]
        fragments.extend(["Report", "GHB", report_token])
        return fragments

    fragments.append(stem)
    return fragments


def build_required_web_filenames(run_date: date) -> list[str]:
    return [
        build_daily_zip_filename(run_date),
        build_indcr_filename(run_date),
        build_report_zip_filename(run_date),
    ]


def build_optional_web_filenames(run_date: date) -> list[str]:
    return [build_gco_filename(run_date)]
