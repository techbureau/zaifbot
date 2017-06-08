from os import environ as env


def preset_keys(key, secret):
    env['ZAIFBOT_KEY'] = key
    env['ZAIFBOT_SECRET'] = secret


def get_keys():
    return env['ZAIFBOT_KEY'], env['ZAIFBOT_SECRET']
