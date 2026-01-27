"""
Timezone Utility Module

Provides IST (Indian Standard Time, UTC+5:30) timezone support across the app.
"""

from datetime import datetime, timezone, timedelta

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> datetime:
    """
    Get current datetime in IST timezone.
    
    Returns:
        datetime: Current time with IST timezone info
    """
    return datetime.now(IST)


def utc_to_ist(dt: datetime) -> datetime:
    """
    Convert a UTC datetime to IST.
    
    Args:
        dt: Datetime object (assumes UTC if naive)
    
    Returns:
        datetime: Converted datetime in IST
    """
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)


def format_ist(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S IST") -> str:
    """
    Format datetime in IST for display.
    
    Args:
        dt: Datetime object
        fmt: Format string (default includes IST label)
    
    Returns:
        str: Formatted datetime string
    """
    ist_dt = utc_to_ist(dt) if dt.tzinfo != IST else dt
    return ist_dt.strftime(fmt)
