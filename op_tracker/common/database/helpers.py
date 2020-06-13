"""
Database helper functions
"""
from op_tracker import WORK_DIR
from op_tracker.common.database.database import get_latest
from op_tracker.utils.data_manager import DataManager


def export_latest():
    """
    Export latest updates from the database to YAML file
    :return:
    """
    latest = get_latest()
    DataManager.write_file(f"{WORK_DIR}/data/latest.yml", latest)
