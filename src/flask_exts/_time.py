"""UTC datetime helpers and a database type that normalizes to UTC.

Application code should use timezone-aware UTC datetimes. Databases whose
timestamp columns do not preserve offsets, such as SQLite and PostgreSQL
``timestamp without time zone``, store the UTC wall time and return naive
values. :class:`UTCDateTime` converts in both directions so callers always see
aware UTC values.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

__all__ = ["UTCDateTime", "ensure_utc", "utc_now"]


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(tz=UTC)


def ensure_utc(value: datetime) -> datetime:
    """Return ``value`` as a timezone-aware UTC datetime.

    Naive values are assumed to be UTC, which is how :class:`UTCDateTime`
    stores timestamps in databases without timezone support.

    Args:
        value: Datetime to normalize.

    Returns:
        datetime: The value converted to UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class UTCDateTime(TypeDecorator[datetime]):
    """Store datetimes as naive UTC and load them as aware UTC."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return ensure_utc(value).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ensure_utc(value)
