import os
import configparser
from os import environ as env
from zaifbot.errors import ZaifBotError


# for trade_api
def set_keys(key, secret):
    env['ZAIFBOT_KEY'] = key
    env['ZAIFBOT_SECRET'] = secret


def get_keys():
    if env.get('ZAIFBOT_KEY') and env.get('ZAIFBOT_SECRET'):
        return env['ZAIFBOT_KEY'], env['ZAIFBOT_SECRET']

    home = os.path.expanduser('~')
    config_file = os.path.join(home, '.zaifbot')
    if os.path.isfile(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config['api_keys']['key'], config['api_keys']['secret']

    raise ZaifBotError('api keys are not set')
