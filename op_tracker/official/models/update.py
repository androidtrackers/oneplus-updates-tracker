"""
OnePlus Device Update representation class
"""
import logging
import re
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup


@dataclass
class Update:
    """
    Update class that represents a device update
    :param device: str - Device Name
    :param code: str - Device code
    :param image: str - Device image URL
    :param version: str - Update version
    :param time: str - Update type
    :param updated: str - Update release date and time
    :param size: str - Update size
    :param link: str - Update Download link
    :param changelog: str - Update changelog
    """
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
        """
        Factory method to create an instance of :class:`Update` from OnePlus updates api response
        :param response: dict - OnePlus updates api response
        :param region: region name of oneplus website
        :return: :class:`Devices` instance
        """
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

    def parse_changelog(self, _changelog: str) -> str:
        """
        Parse the changelog html and return clean string
        :param _changelog: OnePlus API response changelog field
        :return: A clean string of changelog html
        """
        if not _changelog:
            self._logger.warning(f"{self.device} ({self.version}) empty changelog!")
            return ""
        changelog: str = BeautifulSoup(_changelog, 'html.parser').get_text(separator="\n")
        # clean up the text
        changelog: str = re.sub(r'\s\s+', r' ', changelog)
        changelog: str = re.sub(" •", r"\n•", changelog)
        changelog: str = re.sub(r"\s+$", "", changelog)
        changelog: str = re.sub(r"\xa0", "", changelog)
        return changelog

    def __str__(self):
        return f"{self.device} {self.type} {self.version}: {self.link}"
