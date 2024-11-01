from dataclasses import dataclass
from typing import Tuple


@dataclass
class Location:
    name: str
    key: str
    coords: Tuple[float, float]

    @property
    def dict(self):
        return self.__dict__
