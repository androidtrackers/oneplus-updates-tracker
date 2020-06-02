"""
OnePlus devices representation class
"""
from dataclasses import dataclass


@dataclass
class Devices:
    """
    Devices dataclass for representation of devices information
    :param names: list - list of names of devices
    :param codes: list - list of codes of devices
    :param images: list - list of images of devices
    :param item: dict - dictionary of devices names and codes
    """
    names: list
    codes: list
    images: list
    items: dict

    @classmethod
    def from_response(cls, response: list):
        """
        Factory method to create an instance of :class:`Devices` from OnePlus updates api response
        :param response: dict - OnePlus updates api response
        :return: :class:`Devices` instance
        """
        return cls(
            [i.get('phoneName') for i in response],
            [i.get('phoneCode') for i in response],
            [i.get('phoneImage') for i in response],
            {i.get('phoneName'): i.get('phoneCode') for i in response}
        )
