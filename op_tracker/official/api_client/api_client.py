"""
OnePlus Websites Scraper class implementation
"""
import json
from random import randint

from aiohttp import ClientResponse

from op_tracker.common.api_client.common_scraper import CommonClient
from op_tracker.official.models.device import Device


class Website(CommonClient):
    """
    OnePlus Websites Scraper

    This class is used to scrape OnePlus websites.
    It's responsible for interacting with OnePlus websites API in order to:
    - Get devices list.
    - Get device's updates information
    :attr: `region`: str - Website region
    :attr: `base_url`: str - Website base URL
    :attr: `random_int`: str - API magic number. OnePlus Website API requires
    a random integer of 28 digits in request headers and post data.
    :attr: `headers`: dict - HTTP request headers
    :attr: `devices`: list - list of devices available on the website
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
                self.devices = await self._get_json_response(response)

    async def get_updates(self, device: Device):
        """
        Get the latest available updates for a device from the website API.
        :param device: Device - the device object
        :return:a list of the device's available updates information
        """
        data: str = f'-----------------------------' \
                    f'{self.random_int}\nContent-Disposition: form-data; ' \
                    f'name="storeCode"\n\n{self.region}\n' \
                    f'-----------------------------{self.random_int}' \
                    f'\nContent-Disposition: form-data; name="phoneCode"\n\n{device.code}\n' \
                    f'-----------------------------{self.random_int}--'

        async with self.session.post(
                f'{self.base_url}/xman/send-in-repair/find-phone-systems',
                headers=self.headers, data=bytes(data.encode('utf-8'))) as response:
            if response.status == 200:
                return await self._get_json_response(response)

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
