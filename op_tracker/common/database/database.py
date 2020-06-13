"""
Database related functions
"""

from op_tracker.common.database import session
from op_tracker.common.database.models.update import Update

devices = session.query(
    Update.device, Update.region, Update.version,
    Update.branch, Update.type, Update.product
).filter(Update.type == "Full").order_by(
    Update.date.desc()).distinct(Update.product)


def get_latest() -> list:
    latest_updates = session.query(Update).filter(Update.type == "Full").order_by(
        Update.date.desc()).distinct(Update.product).all()
    latest = [{
        "changelog": item.changelog,
        "device": item.device,
        "link": item.link,
        "md5": item.md5,
        "region": item.region,
        "size": item.size,
        "branch": item.branch,
        "date": item.date,
        "version": item.version
    } for item in latest_updates]
    return latest


def get_incremental(version: str) -> Update:
    """
    Get incremental update information of a version
    :type version: str
    :param version: OnePlus software version
    """
    return session.query(Update).filter(
        Update.version == version).filter(Update.type == "Incremental").one_or_none()


def get_version(device: str, branch: str) -> str:
    """
    Get device version example
    :param device: device name
    :type device: str
    :param branch: Update branch
    """
    return session.query(Update.version).filter(
        Update.filename.startswith(device)).filter(Update.branch == branch).first()


def add_to_db(update: Update):
    """Adds an update to the database"""
    session.add(update)
    session.commit()


def already_in_db(md5):
    """
    Check if an update is already in the database
    :param md5: Update file md5
    :return: True if the update is already in the database
    """
    return bool(session.query(Update).filter_by(md5=md5).count() >= 1)
