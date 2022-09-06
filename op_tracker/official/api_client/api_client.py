"""
OnePlus Websites Scraper class implementation
"""
import json
import logging
from datetime import datetime
from typing import Dict, List

from aiohttp import ClientResponse

from op_tracker.common.api_client.common_scraper import CommonClient
from op_tracker.common.database.database import add_to_db, already_in_db
from op_tracker.common.database.models.update import Update
from op_tracker.official.models.device import Device
from op_tracker.utils.helpers import (get_version_from_file,
                                      parse_changelog_from_website)


class APIClient(CommonClient):
    """
    OnePlus Websites API client

    This class is used to get data OnePlus websites API.
    It's responsible for interacting with OnePlus websites API in order to:
    - Get devices list.
    - Get device's updates information
    :attr: `region`: str - Website region
    :attr: `headers`: dict - HTTP request headers
    :meth: `get_devices` - Get all available devices on the website.
    :meth: `get_updates` - Get all updates available for a device.
    """

    def __init__(self, region):
        """
        Website Class constructor
        :param region: OnePlus website region
        """
        super().__init__()
        self.region: str = region
        self.base_url: str = (
            "https://storeapi-na.oneplus.com"
            if self.region != "cn"
            else "https://store.oneplus.com"
        )
        self.headers: Dict[str, str] = {
            # 'authority': 'storeapi-na.oneplus.com',
            "authority": self.base_url.split("/")[-1],
            "content-type": "application/json",
            "origin": "https://www.oneplus.com",
            "referer": "https://www.oneplus.com/",
        }
        self._logger = logging.getLogger(__name__)

    async def get_devices(self):
        """
        Get all available devices list from the website API.
        """
        json_data = json.dumps({"storeCode": self.region})
        async with self.session.post(
                f"{self.base_url}/xman/send-in-repair/find-phone-models",
                headers=self.headers,
                data=json_data,
        ) as response:
            if response.status == 200:
                self.devices = [
                    Device.from_response(item)
                    for item in await self._get_json_response(response)
                ]
                return self.devices

    async def get_updates(self, device: Device, region: dict) -> list:
        """
        Get the latest available updates for a device from the website API.
        :param region: Website region
        :param device: Device - the device object
        :return:a list of the device's available updates information
        """
        updates = []
        device.region = region.get("name")
        # Get latest
        update = await self._fetch(device)
        if update:
            for item in update:
                updates.append(item)
        return updates

    async def _request(self, json_data: str) -> list:
        """
        Perform an OTA request
        :param json_data: OnePlus API request data
        :return: OTA response dictionary
        """
        async with self.session.post(
                f"{self.base_url}/xman/send-in-repair/find-phone-systems",
                headers=self.headers,
                data=json_data,
        ) as response:
            if response.status == 200:
                try:
                    data: dict = json.loads(await response.text())
                    if data["ret"] == 1 and data["errCode"] == 0:
                        return data["data"]
                except json.JSONDecodeError:
                    self._logger.warning(f"Cannot decode JSON response of {data}")
                    return []
            else:
                self._logger.warning(
                    f"Not ok response ({response.reason}): "
                    f"{data}\n{response.content}"
                )

    async def _fetch(self, device: Device) -> List[Update]:
        """
        Fetch an update and add it to the database if new
        :param device: device object
        :return: Update object
        """
        json_data = json.dumps({"storeCode": device.region, "phoneCode": device.code})
        response: list = await self._request(json_data)
        if response:
            updates = []
            for item in response:
                filename = item.get("versionLink").split("/")[-1]
                if not already_in_db(item.get("versionSign").lower()):
                    update = self._parse_response(item, device)
                    add_to_db(update)
                    self._logger.info(f"Added {filename} to db")
                    updates.append(update)
            return updates

    def _parse_response(self, response: dict, device: Device) -> Update:
        """
        Parse the response from th API into an Update object
        :param response: API response dictionary
        :param device: device object
        :return: Update object
        """
        _changelog = response.get("versionLog")
        name = response.get("phoneName")
        filename = response.get("versionLink").split("/")[-1]
        branch = "Stable" if response.get("versionType") == 1 else "Beta"
        version = get_version_from_file(filename, branch)
        if not _changelog:
            self._logger.warning(f"{name} ({version}) empty changelog!")
        return Update(
            device=device.name,
            changelog=parse_changelog_from_website(_changelog),
            changelog_link=None,
            link=response.get("versionLink"),
            region=device.region,
            size=response.get("versionSize"),
            md5=response.get("versionSign").lower(),
            date=datetime.utcfromtimestamp(
                response.get("versionReleaseTime") / 1000
            ).strftime("%Y-%m-%d"),
            version=version if version else response.get("versionNo"),
            type="Full" if "patch" not in filename else "Incremental",
            branch=branch,
            filename=filename,
            insert_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            product=device.get_product(),
        )

    @staticmethod
    async def _get_json_response(_response: ClientResponse):
        """
        Get a JSON response from the HTTP response
        :param _response: ClientResponse: The API response client object
        :return:
        """
        response: dict = json.loads(await _response.text())
        return (
            response["data"]
            if response["ret"] == 1 and response["errCode"] == 0
            else []
        )
