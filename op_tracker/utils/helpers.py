"""OnePlus Updates Tracker helper functions"""
import re
from datetime import datetime

from bs4 import BeautifulSoup
from op_tracker.common.database.database import get_version


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


def parse_changelog_from_website(_changelog: str) -> str:
    """
    Parse the changelog html and return clean string
    :param _changelog: OnePlus API response changelog
    :return: A clean string of changelog html
    """

    changelog: str = BeautifulSoup(_changelog, 'html.parser').get_text(separator="\n")
    # clean up the text
    changelog: str = re.sub(r'\s\s+', r' ', changelog)
    changelog: str = re.sub(" •", r"\n•", changelog)
    changelog: str = re.sub(r"\s+$", "", changelog)
    changelog: str = re.sub(r"\xa0", "", changelog)
    return changelog


def get_version_letter(version: str, branch: str) -> str:
    """
    Get version letter of irregular update version
    :param version: irregular version from zip name
    :param branch: zip file branch
    :return:
    """
    letter = ""
    device = version.split('_')[0].replace("Hydrogen", "").replace("Oxygen", "")
    if (device.startswith("OnePlus5") or device.startswith("OnePlus7")) and branch == "Stable":
        letter = "J"
    if device.startswith("OnePlus5") and branch == "Beta":
        letter = "T"
    if (device.startswith("OnePlus6") or device.startswith("OnePlus7")) and branch == "Stable":
        letter = "J"
    return letter


def get_version_from_file(filename: str, branch: str) -> str:
    version: str = ""
    pattern = re.search(r'_\d{2}\.\w\.\d{2}', filename)
    pattern2 = re.search(r'_\d{2}_OTA_\d{3}_all', filename)
    if pattern:
        version = re.sub('_OTA', '', filename)
        version = re.sub('_all', '', version)
        version = re.sub(r'_[a-z0-9]{16}\.zip', '', version)
    elif pattern2:
        another_version = get_version(filename.split('_')[0], branch)
        if another_version:
            split_version = re.search(r'_OTA_(\d{3})_all', filename).group(1)
            version = re.sub(r'\.\d{2}', f".{split_version[1:]}", another_version.version)
            version = re.sub(r'_\d{3}_', f"_{split_version}_", version)
            version = re.sub(r'_\d{10}_', filename.split('_')[-2], version)
    return version
