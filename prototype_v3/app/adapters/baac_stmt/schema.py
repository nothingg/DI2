from __future__ import annotations

from datetime import date, timedelta


def adjust_to_business_date(run_date: date) -> date:
    if run_date.weekday() == 5:
        return run_date - timedelta(days=1)
    if run_date.weekday() == 6:
        return run_date - timedelta(days=2)
    return run_date


def build_date_token(run_date: date) -> str:
    return run_date.strftime("%Y%m%d")


def build_year_token(run_date: date) -> str:
    return run_date.strftime("%Y")


def build_month_token(run_date: date) -> str:
    return run_date.strftime("%Y%m")


def build_workspace_url() -> str:
    return "https://unicorn.baac.or.th/ws-statement-GHB1/"


def build_year_item_id(run_date: date) -> str:
    return f"item-{build_year_token(run_date)}-cont"


def build_month_item_id(run_date: date) -> str:
    return f"item-{build_month_token(run_date)}-cont"


def build_day_item_id(run_date: date) -> str:
    return f"item-{build_date_token(run_date)}-cont"


def build_expected_filename(run_date: date) -> str:
    return f"GHB1{build_date_token(run_date)}.pdf"


def build_file_row_id(run_date: date) -> str:
    token = build_date_token(run_date)
    return f"item-{token}ghb1{token}pdf-cont"
