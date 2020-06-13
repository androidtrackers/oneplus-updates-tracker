"""
OnePlus Device representation class (Official Website API)
"""
import re
from dataclasses import dataclass


@dataclass
class Device:
    """
    A class representing device information
    :param name: str - the name of the device
    :param code: str - the code of the device (on OnePlus website)
    :param image: str - the image of the device
    :param region: str - region of the device
    :param product: str - product name the device
    """
    name: str
    code: str
    image: str
    region: str
    product: str

    @classmethod
    def from_response(cls, response: dict):
        """
        Factory method to create an instance of :class:`Device` from OnePlus updates api response
        :param response: dict - OnePlus updates api response
        :return: :class:`Device` instance
        """
        if re.match(r'\d\s\w{2,}', response.get('phoneName')):
            name = re.sub(r'\d\w{2,}', r'\d\s\w{2,}', response.get('phoneName'))
        else:
            name = response.get('phoneName')
        return cls(name, response.get('phoneCode'),
                   response.get('phoneImage'), "", "")

    def get_product(self):
        product = None
        device = re.sub(r'OnePlus\s', '', self.name)
        if device in ['1', '2', '3', '3T', '5', '6', '6T', 'X']:
            product = self.name.replace(' ', '')
        elif device == "7" or device == "7 Pro":
            if self.region == "China":
                product = f"{self.name.replace(' ', '')}_CH"
            elif self.region == "EEA":
                product = f"{self.name.replace(' ', '')}_EEA"
            else:
                product = self.name.replace(' ', '')
        elif device == "7T" or device == "7T Pro":
            if self.region == "China":
                product = f"{self.name.replace(' ', '')}_CH"
            else:
                product = self.name.replace(' ', '')
        else:
            if self.region == "Global":
                product = self.name.replace(' ', '')
            elif self.region == "China":
                product = f"{self.name.replace(' ', '')}_CH"
            elif self.region == "EEA" or self.region == "Europe":
                product = f"{self.name.replace(' ', '')}_EEA"
            elif self.region == "India":
                product = f"{self.name.replace(' ', '')}_IND"
        self.product = product
        return product


def __str__(self):
    return f"{self.device} ({self.code})"
