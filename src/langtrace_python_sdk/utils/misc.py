
from datetime import datetime


def to_iso_format(value):
    return None if value is None else value.isoformat(timespec='microseconds') + 'Z' if isinstance(value, datetime) else None
