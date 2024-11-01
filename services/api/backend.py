from services.api.Geolocation.api import Geolocation
from services.api.Weather.api import Weather
from services.common import BaseService


class Backend(BaseService):
    """
    Бэкенд для работы с API "AccuWeather"
    """
    def __init__(self, address: str, api_key: str):
        super().__init__(address, api_key)

        self.geolocation: Geolocation = Geolocation(api_key=api_key, address=address)
        self.weather: Weather = Weather(api_key=api_key, address=address)
