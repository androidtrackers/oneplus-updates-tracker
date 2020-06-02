"""
OnePlus Device representation class
"""
from dataclasses import dataclass


@dataclass
class Device:
    """
    A class representing device information
    :param name: str - the name of the device
    :param code: str - the code of the device (on OnePlus website)
    :param image: str - the image of the device
    """
    name: str
    code: str
    image: str

    @classmethod
    def from_response(cls, response: dict):
        """
        Factory method to create an instance of :class:`Device` from OnePlus updates api response
        :param response: dict - OnePlus updates api response
        :return: :class:`Device` instance
        """
        return cls(response.get('phoneName'), response.get('phoneCode'), response.get('phoneImage'))


def __str__(self):
    return f"{self.device} ({self.code})"
