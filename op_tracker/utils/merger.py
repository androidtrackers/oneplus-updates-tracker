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
