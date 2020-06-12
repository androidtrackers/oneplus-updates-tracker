"""OnePlus Updates Tracker helper functions"""
import re
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


def parse_changelog(changelog: str) -> str:
    """
    Parse the changelog markdown and return clean string
    :param changelog: OnePlus API response changelog
    :return: A clean string of changelog response
    """
    changelog = re.sub(r'#', r'', changelog)
    changelog = changelog.replace('[www.oneplus.com]{http://www.oneplus.com/}', '')
    changelog = re.sub('\\\\', '', changelog)
    changelog = re.sub('\n\n+', r'\n', changelog)
    changelog = re.sub(' +', ' ', changelog)
    changelog = changelog.strip()
    return changelog
