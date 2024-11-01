from dataclasses import dataclass
from os import getenv
from string import digits

from dotenv import load_dotenv


@dataclass
class Config:
    api_key: str
    host: str
    port: int
    api_url: str
    bot_token: str


def load_config() -> Config:
    load_dotenv()
    api_key = getenv('API_KEY', 'TEST_KEY')
    host = getenv('HOST', default='127.0.0.1')
    port = getenv('PORT', default=8080)
    api_url = getenv('API_URL', default='http://dataservice.accuweather.com/')
    bot_token = getenv('BOT_TOKEN', default=None)
    if set(str(port)) < set(digits):
        port = int(port)
    else:
        raise ValueError('Invalid port')
    conf = Config(api_key=api_key,
                  host=host,
                  port=port,
                  api_url=api_url,
                  bot_token=bot_token)

    return conf