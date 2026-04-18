from __future__ import annotations

from datetime import date


def build_date_token(run_date: date) -> str:
    return run_date.strftime("%Y%m%d")


def build_year_token(run_date: date) -> str:
    return run_date.strftime("%Y")


def build_month_token(run_date: date) -> str:
    return run_date.strftime("%Y%m")


def build_workspace_url() -> str:
    return "https://unicorn.baac.or.th/ws-payment-l001/"


def build_year_item_id(run_date: date) -> str:
    return f"item-{build_year_token(run_date)}"


def build_month_item_id(run_date: date) -> str:
    return f"item-{build_month_token(run_date)}"


def build_day_item_id(run_date: date) -> str:
    return f"item-{build_date_token(run_date)}"


def build_pdf_row_id(run_date: date, report_code: str) -> str:
    token = build_date_token(run_date)
    normalized = report_code.lower()
    return f"item-{token}{normalized}l001{token}pdf"


def build_file_row_id(run_date: date, file_name: str) -> str:
    token = build_date_token(run_date)
    normalized = file_name.lower().replace(".", "")
    return f"item-{token}{normalized}"


def build_expected_pdf_filename(run_date: date, report_code: str) -> str:
    token = build_date_token(run_date)
    normalized = report_code.upper()
    return f"{normalized}_L001_{token}.pdf"


def build_redcr_filename(run_date: date) -> str:
    return f"REDCR0000000003300000205{build_date_token(run_date)}001.zip"


def build_servu_filename(run_date: date) -> str:
    return f"INDCR0000000003300000205{build_date_token(run_date)}001.TXT"
