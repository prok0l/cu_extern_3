from dataclasses import dataclass
from datetime import date
from enum import Enum

from entities.errors.weather_error import *
from entities.location import Location


class DayPart(Enum):
    DAY: str = 'Day'
    NIGHT: str = 'Night'


class Temperature:
    def __init__(self, min_temp, max_temp):
        self.min_temp: float = min_temp
        self.max_temp: float = max_temp

    @property
    def temp(self):
        return (self.min_temp + self.max_temp) / 2


@dataclass
class WeatherInfo:
    day: date
    day_part: DayPart
    location: Location
    temp: float
    wind_speed: float
    rain_p: int
    humidity: float

    msg: str = ''
    error_code: str = ''

    def validate(self):
        validator = WeatherValidator()
        return validator.validate(self)

    def make_msg(self):
        try:
            if self.validate():
                self.msg = 'Всё супер'

        except InvalidTempValue:
            self.error_code = 'bg-danger'
            self.msg = 'ОШИБКА ПОЛУЧЕНИЯ ДАННЫХ ТЕМПЕРАТУРЫ'
        except InvalidHumidityValue:
            self.error_code = 'bg-danger'
            self.msg = 'ОШИБКА ПОЛУЧЕНИЯ ДАННЫХ ВЛАЖНОСТИ'
        except InvalidRainValue:
            self.error_code = 'bg-danger'
            self.msg = 'ОШИБКА ПОЛУЧЕНИЯ ДАННЫХ ДОЖДЯ'
        except InvalidWindSpeedValue:
            self.error_code = 'bg-danger'
            self.msg = 'ОШИБКА ПОЛУЧЕНИЯ ДАННЫХ СКОРОСТИ ВЕТРА'
        except UnfavorableWeather as e:
            self.error_code = 'bg-warning'
            self.msg = str(e)


class WeatherValidator:
    TEMP = (0, 35)
    WIND_SPEED = (-1, 50)
    RAIN_P = (-1, 70)
    HUMIDITY = (20, -1)

    def __validate_temp(self, temp):
        if temp < -100 or temp > 60:
            raise InvalidTempValue('Invalid temperature value')
        if self.TEMP[0] == -1 or temp >= self.TEMP[0]:
            if self.TEMP[0] == -1 or temp <= self.TEMP[1]:
                return True
        return False

    def __validate_wind(self, speed):
        if speed < 0 or speed > 520:
            raise InvalidWindSpeedValue('Invalid wind speed value')

        if self.WIND_SPEED[0] == -1 or speed >= self.WIND_SPEED[0]:
            if self.WIND_SPEED[1] == -1 or speed <= self.WIND_SPEED[1]:
                return True
        return False

    def __validate_rain(self, rain):
        if rain > 100 or rain < 0:
            raise InvalidRainValue('Invalid rain value')

        if self.RAIN_P[0] == -1 or rain >= self.RAIN_P[0]:
            if self.RAIN_P[1] == -1 or rain <= self.RAIN_P[1]:
                return True
        return False

    def __validate_humidity(self, humidity):
        if humidity > 100 or humidity < 0:
            raise InvalidHumidityValue('Invalid humidity value')

        if self.HUMIDITY[0] == -1 or humidity >= self.HUMIDITY[0]:
            if self.HUMIDITY[1] == -1 or humidity <= self.HUMIDITY[1]:
                return True
        return False

    def validate(self, weather: WeatherInfo) -> bool:
        if not self.__validate_temp(weather.temp):
            raise UnfavorableWeather('Неблагоприятная температура')
        if not self.__validate_rain(weather.rain_p):
            raise UnfavorableWeather('Неприятный дождь')
        if not self.__validate_wind(weather.wind_speed):
            raise UnfavorableWeather('Неприятный ветер')
        if not self.__validate_humidity(weather.humidity):
            raise UnfavorableWeather('Влажность не очень')
        return True
