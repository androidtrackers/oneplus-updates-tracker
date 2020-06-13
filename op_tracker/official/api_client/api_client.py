"""
OnePlus Websites Scraper class implementation
"""
import json
import logging
from datetime import datetime
from random import randint
from typing import List

from aiohttp import ClientResponse
from op_tracker.common.api_client.common_scraper import CommonClient
from op_tracker.common.database.database import already_in_db, add_to_db
from op_tracker.common.database.models.update import Update
from op_tracker.official.models.device import Device
from op_tracker.utils.helpers import parse_changelog_from_website, get_version_from_file


class APIClient(CommonClient):
    """
    OnePlus Websites API client

    This class is used to get data OnePlus websites API.
    It's responsible for interacting with OnePlus websites API in order to:
    - Get devices list.
    - Get device's updates information
    :attr: `region`: str - Website region
    :attr: `random_int`: str - API magic number. OnePlus Website API requires
    a random integer of 28 digits in request headers and post data.
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
        self.base_url: str = "https://store.oneplus.com" \
            if self.region == "cn" else "https://www.oneplus.com"
        self.random_int: str = str(randint(10 ** 28, 10 ** 29 - 1))
        self.headers: dict = {
            'Content-Type': f'multipart/form-data; '
                            f'boundary=---------------------------{self.random_int}',
            'Connection': 'keep-alive',
        }
        self._logger = logging.getLogger(__name__)

    async def get_devices(self):
        """
        Get all available devices list from the website API.
        """
        data: str = f'-----------------------------' \
                    f'{self.random_int}\nContent-Disposition: form-data; ' \
                    f'name="storeCode"\n\n{self.region}\n' \
                    f'-----------------------------{self.random_int}--'

        async with self.session.post(
                f'{self.base_url}/xman/send-in-repair/find-phone-models',
                headers=self.headers, data=bytes(data.encode('utf-8'))) as response:
            if response.status == 200:
                self.devices = [Device.from_response(item) for item in await self._get_json_response(response)]
                return self.devices

    async def get_updates(self, device: Device, region: dict) -> list:
        """
        Get the latest available updates for a device from the website API.
        :param region: Website region
        :param device: Device - the device object
        :return:a list of the device's available updates information
        """
        updates = []
        device.region = region.get('name')
        # Get latest
        update = await self._fetch(device)
        if update:
            for item in update:
                updates.append(item)
        return updates

    async def _request(self, data: str) -> list:
        """
        Perform an OTA request
        :param data: OnePlus API request data
        :return: OTA response dictionary
        """
        encoded_data = bytes(data.encode('utf-8'))
        async with self.session.post(
                f'{self.base_url}/xman/send-in-repair/find-phone-systems',
                headers=self.headers, data=encoded_data) as response:
            if response.status == 200:
                try:
                    data: dict = json.loads(await response.text())
                    if data['ret'] == 1 and data['errCode'] == 0:
                        return data['data']
                except json.JSONDecodeError:
                    self._logger.warning(f"Cannot decode JSON response of {data}")
                    return []
            else:
                self._logger.warning(f"Not ok response ({response.reason}): "
                                     f"{data}\n{response.content}")

    async def _fetch(self, device: Device) -> List[Update]:
        """
        Fetch an update and add it to the database if new
        :param device: device object
        :return: Update object
        """
        data: str = f'-----------------------------' \
                    f'{self.random_int}\nContent-Disposition: form-data; ' \
                    f'name="storeCode"\n\n{self.region}\n' \
                    f'-----------------------------{self.random_int}' \
                    f'\nContent-Disposition: form-data; name="phoneCode"\n\n{device.code}\n' \
                    f'-----------------------------{self.random_int}--'
        response: list = await self._request(data)
        if response:
            updates = []
            for item in response:
                filename = item.get('versionLink').split('/')[-1]
                if not already_in_db(item.get('versionSign').lower()):
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
        _changelog = response.get('versionLog')
        name = response.get('phoneName')
        filename = response.get('versionLink').split('/')[-1]
        branch = "Stable" if response.get('versionType') == 1 else "Beta"
        version = get_version_from_file(filename, branch)
        if not _changelog:
            self._logger.warning(f"{name} ({version}) empty changelog!")
        return Update(
            device=device.name,
            changelog=parse_changelog_from_website(_changelog),
            changelog_link=None,
            link=response.get('versionLink'),
            region=device.region,
            size=response.get('versionSize'),
            md5=response.get('versionSign').lower(),
            date=datetime.utcfromtimestamp(response.get('versionReleaseTime') / 1000).strftime(
                '%Y-%m-%d'),
            version=version if version else response.get('versionNo'),
            type="Full" if "patch" not in filename else "Incremental",
            branch=branch,
            filename=filename,
            insert_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            product=device.get_product())

    @staticmethod
    async def _get_json_response(_response: ClientResponse):
        """
        Get a JSON response from the HTTP response
        :param _response: ClientResponse: The API response client object
        :return:
        """
        response: dict = json.loads(await _response.text())
        if response['ret'] == 1 and response['errCode'] == 0:
            return response['data']
