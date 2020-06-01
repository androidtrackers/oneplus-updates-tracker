from dataclasses import dataclass


@dataclass
class Device:
    name: str
    code: str
    image: str

    @classmethod
    def from_response(cls, response: dict):
        return cls(response.get('phoneName'), response.get('phoneCode'), response.get('phoneImage'))


def __str__(self):
    return f"{self.device} ({self.code})"
