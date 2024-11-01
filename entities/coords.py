from dataclasses import dataclass


@dataclass
class Coords:
    latitude: float
    longitude: float

    def __str__(self):
        return f'{self.latitude},{self.longitude}'


@dataclass
class LocationName:
    name: str

    def __str__(self):
        return self.name


@dataclass
class Points:
    start: Coords | LocationName
    end: Coords | LocationName
