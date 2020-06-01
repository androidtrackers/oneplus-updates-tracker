from dataclasses import dataclass


@dataclass
class Devices:
    names: list
    codes: list
    images: list
    items: dict

    @classmethod
    def from_response(cls, response: list):
        return cls(
            [i.get('phoneName') for i in response],
            [i.get('phoneCode') for i in response],
            [i.get('phoneImage') for i in response],
            {i.get('phoneName'): i.get('phoneCode') for i in response}
        )
