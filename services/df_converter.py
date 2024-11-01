from typing import List

import pandas as pd

from entities.weather import WeatherInfo


day_part = {
    'Day': 'День',
    'Night': 'Ночь'
}


def convert_to_dict(weather_data: List[List[WeatherInfo]]) -> List[dict]:
    records = list()

    for daily_weather in weather_data:
        for weather_info in daily_weather:
            record = {
                'date': f'{weather_info.day.strftime("%d.%m.%Y")} {day_part[weather_info.day_part]}',
                'location_name': weather_info.location.name,
                'location_key': weather_info.location.key,
                'temp': weather_info.temp,
                'wind_speed': weather_info.wind_speed,
                'rain_p': weather_info.rain_p,
                'humidity': weather_info.humidity,
            }
            records.append(record)

    # df = pd.DataFrame(records)
    return records