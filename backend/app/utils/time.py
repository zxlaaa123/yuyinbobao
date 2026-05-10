from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return naive UTC for SQLite storage; API clients should treat it as UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def utc_today_start() -> datetime:
    return utc_now().replace(hour=0, minute=0, second=0, microsecond=0)


def to_utc_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")
