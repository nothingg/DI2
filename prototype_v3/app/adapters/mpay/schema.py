from __future__ import annotations

from datetime import date


def build_date_token(run_date: date) -> str:
    return run_date.strftime("%Y%m%d")


def build_text_filename(run_date: date) -> str:
    return f"AIS{build_date_token(run_date)}.log"


def build_xml_filename(run_date: date) -> str:
    return f"AIS{build_date_token(run_date)}.xml"


def build_servu_filename(run_date: date) -> str:
    return f"INDCR0000000003300000221{build_date_token(run_date)}001.TXT"


def build_xml_view_selector(run_date: date) -> str:
    xml_name = build_xml_filename(run_date)
    return f"input[onclick*=\"viewReport('{xml_name}')\"]"
