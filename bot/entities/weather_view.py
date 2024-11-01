from typing import List

from entities.location import Location
from entities.weather import WeatherInfo

day_part = {
    'Day': 'День',
    'Night': 'Ночь'
}


class WeatherView:
    def __init__(self, cities: List[Location], data: dict, duration: int):
        self.cities = cities
        self.data = data
        self.duration = duration

    def as_view(self):
        msgs = list()
        for city in self.cities:
            msg = f'*{city.name}*\n\n'
            weathers: List[WeatherInfo] = self.data.get(city.key)[:2 * self.duration]
            for weather in weathers:
                msg += (f'Дата: {weather.day.strftime("%d.%m.%Y")} {day_part[weather.day_part]}\n'
                        f'Температура: {round(weather.temp, 2)}°C\n'
                        f'Скорость ветра: {round(weather.wind_speed, 2)} км/ч\n'
                        f'Вероятность осадков: {round(weather.rain_p, 2)}%\n'
                        f'Влажность: {round(weather.humidity, 2)}%\n\n')
            msgs.append(msg)
        return msgs
