"""OnePlus Updates Tracker helper functions"""
from datetime import datetime


def is_newer_datetime(old_datetime: int, new_datetime: int) -> bool:
    """
    Check if a datetime is newer than another
    :param new_datetime: A datetime in posix time format
    :param old_datetime: A datetime in posix time format
    """
    return bool(
        datetime.strptime(new_datetime, '%d-%m-%Y') >= datetime.strptime(old_datetime, '%d-%m-%Y')
    )
