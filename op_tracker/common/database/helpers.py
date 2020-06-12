"""
Database helper functions
"""
from op_tracker import WORK_DIR
from op_tracker.common.database.database import get_latest
from op_tracker.utils.data_manager import DataManager


def db_to_yaml():
    """
    Export latest updates from the database to YAML file
    :return:
    """
    latest = get_latest()
    DataManager.write_file(f"{WORK_DIR}/data/updater/latest.yml", latest)
