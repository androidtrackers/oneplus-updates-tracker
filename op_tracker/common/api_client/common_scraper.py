"""
OnePlus Websites common API Client class implementation
"""

from aiohttp import ClientSession


class CommonClient:
    """
    Base Scraper class

    This class is used to scrape OnePlus websites.
    It's responsible for interacting with OnePlus websites API in order to:
    - Get devices list.
    - Get device's updates information
    :attr: `session`: ClientSession - aiohttp client session object
    :attr: `base_url`: str - Website base URL
    :attr: `devices`: list - list of devices available on the website
    """

    def __init__(self):
        """
        Website Class constructor
        :param region: OnePlus website region
        """
        self.session: ClientSession = ClientSession()
        self.base_url: str = ""
        self.devices: list = []

    async def close(self):
        """
        Closes the connection of aiohttp client
        :return:
        """
        await self.session.close()
