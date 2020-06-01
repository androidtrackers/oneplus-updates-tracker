from glob import glob
from pathlib import Path
from shutil import copyfile

import yaml

from op_tracker.utils.helpers import is_newer_datetime


class DataManager:
    def __init__(self, data, file):
        self.data: dict = data
        self.file: Path = Path(file)
        self.backup_file: Path = Path(f"{self.file}.bak")
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self.file.touch()

    def save(self):
        self.write_file(self.file, self.data)

    @staticmethod
    def write_file(file, data):
        with open(f"{file}", "w") as out:
            yaml.dump(data, out, allow_unicode=True)

    @staticmethod
    def read_file(file):
        with open(file, "r") as f:
            return yaml.load(f, yaml.FullLoader)

    def backup(self):
        copyfile(self.file, self.backup_file)
        return self.backup_file

    @staticmethod
    def backup_all(directory):
        for item in glob(directory):
            copyfile(f"{item}", f"{item}.bak")

    def is_new_version(self):
        if "version" in self.data.keys() and self.backup_file.exists():
            old: dict = self.read_file(self.backup_file)
            if not old:
                return True
            return bool(
                self.data['version'] != old['version']
                and is_newer_datetime(old['updated'], self.data['updated'])
            )

    def diff_dicts(self):
        old: dict = self.read_file(self.backup_file)
        if not old:
            return {}
        return {key: value for key, value in self.data.items() if key not in old.keys()}
