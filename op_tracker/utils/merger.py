"""YAML files merge functions"""
from glob import glob

from op_tracker import WORK_DIR
from op_tracker.utils.data_manager import DataManager


def merge_devices(regions: dict) -> list:
    """
    Merge YAML files of regions information
    :param regions: a dictionary of regions
    :return: a list of regions
    """
    devices = set()
    for region_code in regions.keys():
        data: dict = DataManager.read_file(f"{WORK_DIR}/data/{region_code}/{region_code}.yml")
        for item in data.keys():
            devices.add(item)
    devices = sorted(list(devices))
    DataManager.write_file(f"{WORK_DIR}/data/devices.yml", devices)
    return devices


def merge_updates(devices: list):
    """
    Merge updates of a list of regions
    :param devices: a list of devices
    :return: None
    """
    for device in devices:
        all_updates = []
        updates = glob(f"{WORK_DIR}/data/*/*/{device}.yml")
        for update in updates:
            data = DataManager.read_file(update)
            all_updates.append(data)
        DataManager.write_file(f"{WORK_DIR}/data/latest/{device}.yml", all_updates)
