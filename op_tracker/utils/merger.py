from glob import glob

from op_tracker import WORK_DIR
from op_tracker.utils.data_manager import DataManager


def merge_devices(regions: dict):
    devices = set()
    for region_code in regions.keys():
        data: dict = DataManager.read_file(f"{WORK_DIR}/data/{region_code}/{region_code}.yml")
        for item in data.keys():
            devices.add(item)
    devices = sorted(list(devices))
    DataManager.write_file(f"{WORK_DIR}/data/devices.yml", devices)
    return devices


def merge_updates(devices: list):
    for device in devices:
        all_updates = []
        updates = glob(f"{WORK_DIR}/data/*/*/{device}.yml")
        for update in updates:
            data = DataManager.read_file(update)
            all_updates.append(data)
        DataManager.write_file(f"{WORK_DIR}/data/latest/{device}.yml", all_updates)
