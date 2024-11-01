import socket

import requests

from entities.coords import Coords, LocationName
from entities.errors.api_error import APIError, APIAuthorizationError, APINumberOfRequests
from entities.location import Location
from services.common import BaseService


class Geolocation(BaseService):
    def __init__(self,
                 api_key: str,
                 address: str = 'http://dataservice.accuweather.com/'):
        super().__init__(address, api_key)

    def get_location_key(self, location: Coords | LocationName):
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
        except socket.error as ex:
            raise ConnectionError('No internet connection')

        if isinstance(location, Coords):
            return self.get_key_by_coords(location)
        elif isinstance(location, LocationName):
            return self.get_key_by_location(location)
        else:
            raise ValueError('Invalid type')

    def get_key_by_location(self, location_name: LocationName):
        try:
            req = requests.get(url=f'{self.address}locations/v1/cities/search',
                               params={
                                   'apikey': self.api_key,
                                   'q': location_name.name,
                                   'language': 'en-us',
                                   'details': 'true'
                               })
            res = req.json()
            if isinstance(res, dict) and res.get('Message', None) == 'Api Authorization failed':
                raise APIAuthorizationError('Api Authorization failed')
            elif isinstance(res, dict) and res.get('Message', None) == ('The allowed number'
                                                                        ' of requests has been exceeded.'):
                raise APINumberOfRequests('The allowed number of requests has been exceeded.')
            data = res[0]
            return Location(key=data['Key'],
                            name=data['LocalizedName'],
                            coords=(data['GeoPosition']['Latitude'],
                                    data['GeoPosition']['Longitude']))
        except APIAuthorizationError as e:
            raise APIAuthorizationError(e)
        except APINumberOfRequests as e:
            raise APINumberOfRequests(e)
        except Exception as e:
            raise APIError(e)

    def get_key_by_coords(self, coords: Coords):
        try:
            req = requests.get(url=f'{self.address}locations/v1/cities/geoposition/search',
                               params={
                                   'apikey': self.api_key,
                                   'q': str(coords),
                                   'language': 'en-us',
                                   'details': 'true',
                                   'toplevel': 'false'
                               })
            res = req.json()
            if isinstance(res, dict) and res.get('Message', None) == 'Api Authorization failed':
                raise APIAuthorizationError('Api Authorization failed')
            elif isinstance(res, dict) and res.get('Message', None) == ('The allowed number'
                                                                        ' of requests has been exceeded.'):
                raise APINumberOfRequests('The allowed number of requests has been exceeded.')

            data = res

            return Location(key=data['Key'],
                            name=data['LocalizedName'],
                            coords=(coords.latitude, coords.longitude))

        except APIAuthorizationError as e:
            raise APIAuthorizationError(e)
        except APINumberOfRequests as e:
            raise APINumberOfRequests(e)
        except Exception as e:
            raise APIError(e)
