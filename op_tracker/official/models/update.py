from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
import re
import logging


@dataclass
class Update:
    device: str
    code: str
    image: str
    region: str
    version: str
    type: str
    updated: str
    size: str
    md5: str
    link: str
    changelog: str
    _logger = logging.getLogger(__name__)

    @classmethod
    def from_response(cls, response: dict, region: str):
        return cls(
            response.get('phoneName'),
            response.get('phoneCode'),
            response.get('phoneImage'),
            region,
            response.get('versionNo'),
            "Stable" if response.get('versionType') == 1 else "Beta",
            datetime.utcfromtimestamp(response.get('versionReleaseTime') / 1000).strftime(
                '%d-%m-%Y'),
            response.get('versionSize'),
            response.get('versionSign'),
            response.get('versionLink'),
            cls.parse_changelog(cls, response.get('versionLog'))
        )

    def parse_changelog(self, _changelog: str):
        if not _changelog:
            self._logger.warning(f"{self.device} ({self.version}) empty changelog!")
            return
        changelog: str = BeautifulSoup(_changelog, 'html.parser').get_text(separator="\n")
        # clean up the text
        changelog: str = re.sub(r'\s\s+', r' ', changelog)
        changelog: str = re.sub(" •", r"\n•", changelog)
        changelog: str = re.sub(r"\s+$", "", changelog)
        changelog: str = re.sub(r"\xa0", "", changelog)
        return changelog

    def __str__(self):
        return f"{self.device} {self.type} {self.version}: {self.link}"
