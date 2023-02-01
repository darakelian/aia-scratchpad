import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, Any, Optional


def make_date_range(start: datetime, end: datetime) -> Iterator[datetime]:
    while start <= end:
        yield start
        start += timedelta(days=1)


def get_safe_datetime(data_dict: dict[str, Any], key_name: str) -> datetime:
    """
    Attempts to get a date from a dict. If key doesnt exist or date is invalid
    this will return UNIX epoch. Assumes dates will be in ISO format
    """
    try:
        val = data_dict.get(key_name)
        return datetime.fromisoformat(val)
    except ValueError or TypeError:
        return datetime(1970, 1, 1, 0, 0, 0)


def path(arg_string: str) -> Path:
    return Path(arg_string)


def iso_date(arg_string: str) -> Optional[datetime]:
    return datetime.strptime(arg_string, "%Y%m%d")


def eprint(*args, sep=' ', end='\n') -> None:
    print(*args, sep=sep, end=end, file=sys.stderr)
