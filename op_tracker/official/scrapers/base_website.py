import json
from random import randint

from aiohttp import ClientSession, ClientResponse

from op_tracker.official.models.device import Device


class Scraper:
    def __init__(self, region):
        self.session: ClientSession = ClientSession()
        self.region: str = region
        self.base_url: str = "https://store.oneplus.com" if self.region == "cn" else "https://www.oneplus.com"
        self.random_int: str = str(randint(10 ** 28, 10 ** 29 - 1))
        self.headers: dict = {
            'Content-Type': f'multipart/form-data; boundary=---------------------------{self.random_int}',
            'Connection': 'keep-alive',
        }
        self.devices: list = []

    async def get_devices(self):
        data: str = f'-----------------------------{self.random_int}\nContent-Disposition: form-data; ' \
                    f'name="storeCode"\n\n{self.region}\n-----------------------------{self.random_int}--'

        async with self.session.post(f'{self.base_url}/xman/send-in-repair/find-phone-models',
                                     headers=self.headers, data=bytes(data.encode('utf-8'))) as response:
            if response.status == 200:
                self.devices = await self._get_json_response(response)

    async def get_updates(self, device: Device):
        data: str = f'-----------------------------{self.random_int}\nContent-Disposition: form-data; ' \
                    f'name="storeCode"\n\n{self.region}\n-----------------------------{self.random_int}' \
                    f'\nContent-Disposition: form-data; name="phoneCode"\n\n{device.code}\n' \
                    f'-----------------------------{self.random_int}--'

        async with self.session.post(f'{self.base_url}/xman/send-in-repair/find-phone-systems',
                                     headers=self.headers, data=bytes(data.encode('utf-8'))) as response:
            if response.status == 200:
                return await self._get_json_response(response)

    @staticmethod
    async def _get_json_response(_response: ClientResponse):
        response: dict = json.loads(await _response.text())
        if response['ret'] == 1 and response['errCode'] == 0:
            return response['data']

    async def close(self):
        await self.session.close()
