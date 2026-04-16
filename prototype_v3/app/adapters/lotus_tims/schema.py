from __future__ import annotations

from datetime import date, timedelta

_MONTH_ABBR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def build_lookup_date(run_date: date) -> date:
    return run_date + timedelta(days=1)


def build_lookup_label(run_date: date) -> str:
    lookup_date = build_lookup_date(run_date)
    return f"{lookup_date.day:02d}-{_MONTH_ABBR[lookup_date.month]}-{lookup_date.year}"
