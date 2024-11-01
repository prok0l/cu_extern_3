from datetime import datetime
from typing import List

import requests

from entities.errors.api_error import APIError, APIAuthorizationError, APINumberOfRequests
from entities.location import Location
from entities.weather import WeatherInfo, Temperature, DayPart
from services.common import BaseService


class Weather(BaseService):
    def __init__(self,
                 api_key: str,
                 address: str = 'http://dataservice.accuweather.com/'):
        super().__init__(address, api_key)

    def get_weather(self, location: Location) -> List[WeatherInfo]:
        try:
            req = requests.get(url=f'{self.address}forecasts/v1/daily/5day/{location.key}',
                               params={
                                   'apikey': self.api_key,
                                   'language': 'en-us',
                                   'details': 'true',
                                   'metric': 'true'
                               })
            res = req.json()
            if isinstance(res, dict) and res.get('Message', None) == 'Api Authorization failed':
                raise APIAuthorizationError('Api Authorization failed')
            elif isinstance(res, dict) and res.get('Message', None) == ('The allowed number'
                                                                        ' of requests has been exceeded.'):
                raise APINumberOfRequests('The allowed number of requests has been exceeded.')

            data = res

            weathers: List[WeatherInfo] = list()
            for day in data['DailyForecasts']:
                for day_part in DayPart:
                    weather = WeatherInfo(rain_p=day[day_part.value]['RainProbability'],
                                          humidity=day[day_part.value]['RelativeHumidity']['Average'],
                                          wind_speed=day[day_part.value]['Wind']['Speed']['Value'],
                                          temp=Temperature(
                                              min_temp=day['Temperature']['Minimum']['Value'],
                                              max_temp=day['Temperature']['Maximum']['Value']
                                          ).temp,
                                          day=datetime.fromisoformat(day['Date']).date(),
                                          location=location,
                                          day_part=day_part.value)
                    weather.make_msg()

                    weathers.append(weather)
            return weathers

        except APIAuthorizationError as e:
            raise APIAuthorizationError(e)
        except APINumberOfRequests as e:
            raise APINumberOfRequests(e)
        except Exception as e:
            raise APIError(e)
