from os import environ as env
from zaifbot.errors import ZaifBotError


# for trade_api
def set_keys(key, secret):
    env['ZAIFBOT_KEY'] = key
    env['ZAIFBOT_SECRET'] = secret


def get_keys():
    if not env.get('ZAIFBOT_KEY') or not env.get('ZAIFBOT_SECRET'):
        raise ZaifBotError('api keys are not set')
    return env['ZAIFBOT_KEY'], env['ZAIFBOT_SECRET']
