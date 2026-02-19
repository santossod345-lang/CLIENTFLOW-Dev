from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple


_PERIOD_ALIASES = {
    "hoje": "today",
    "today": "today",
    "7": "7d",
    "7d": "7d",
    "7dias": "7d",
    "7_days": "7d",
    "30": "30d",
    "30d": "30d",
    "30dias": "30d",
    "30_days": "30d",
    "mes": "month",
    "mês": "month",
    "month": "month",
    "mes_atual": "month",
    "current_month": "month",
}


def normalize_period(period: Optional[str], default: str = "7d") -> str:
    if not period:
        return default
    key = str(period).strip().lower()
    return _PERIOD_ALIASES.get(key, key)


@dataclass(frozen=True)
class DateRange:
    start_date: datetime
    end_date: datetime
    start_date_previous: datetime
    end_date_previous: datetime


def get_date_range(period: str, now: Optional[datetime] = None) -> DateRange:
    """Return current period start/end and previous period start/end.

    - end_date is 'now'
    - previous period has the same duration and ends at start_date
    """
    now_dt = now or datetime.today()
    p = normalize_period(period)

    if p == "today":
        start = now_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif p == "7d":
        start = (now_dt - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif p == "30d":
        start = (now_dt - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif p == "month":
        start = now_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = (now_dt - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    end = now_dt
    duration = end - start
    prev_end = start
    prev_start = start - duration

    return DateRange(
        start_date=start,
        end_date=end,
        start_date_previous=prev_start,
        end_date_previous=prev_end,
    )


def calculate_percentage_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    return ((current - previous) / previous) * 100.0


def build_metric_change(current: float, previous: float) -> dict:
    return {
        "current": current,
        "previous": previous,
        "percentage": round(calculate_percentage_change(current, previous), 1),
    }


def parse_brl_number(value) -> float:
    """Best-effort BRL parsing for legacy data (used only as a fallback)."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value).strip()
    if not raw:
        return 0.0
    raw = raw.replace("R$", "").strip()
    raw = re.sub(r"[^0-9,\.\-]", "", raw)
    if not raw or raw == "-":
        return 0.0

    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")

    try:
        return float(raw)
    except ValueError:
        return 0.0
