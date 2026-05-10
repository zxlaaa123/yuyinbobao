from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def utc_today_start() -> datetime:
    return utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
