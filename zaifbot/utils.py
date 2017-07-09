from os import environ as env
from zaifbot.common.notifier import SlackNotifier


def send_slack_message(slack_token, channel_id, message, username):
    slack_notifier = SlackNotifier(slack_token)
    return slack_notifier.send_message(channel_id, message, username)


def preset_keys(key, secret):
    env['ZAIFBOT_KEY'] = key
    env['ZAIFBOT_SECRET'] = secret


def get_keys():
    return env['ZAIFBOT_KEY'], env['ZAIFBOT_SECRET']


def merge_dict(base_dict, *dicts):
    for dic in dicts:
        base_dict.update(dic) or base_dict
    return base_dict
