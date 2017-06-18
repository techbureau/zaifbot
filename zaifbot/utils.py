from os import environ as env
from zaifbot.bot_common.slack_notifier import SlackNotifier
from zaifbot.bot_common.bot_const import UTC_JP_DIFF, PERIOD_SECS


def send_slack_message(slack_token, channel_id, message, username):
    slack_notifier = SlackNotifier(slack_token)
    return slack_notifier.send_message(channel_id, message, username)


def preset_keys(key, secret):
    env['ZAIFBOT_KEY'] = key
    env['ZAIFBOT_SECRET'] = secret


def get_keys():
    return env['ZAIFBOT_KEY'], env['ZAIFBOT_SECRET']


# TODO: クラスを作成するか検討
# 数値のずれを見つけ次第修正
def truncate_time_at_period(to_epoch_time, period):
    if PERIOD_SECS[period] > PERIOD_SECS['1h']:
        end_time = to_epoch_time - ((to_epoch_time + UTC_JP_DIFF) % PERIOD_SECS[period])
    else:
        end_time = to_epoch_time - (to_epoch_time % PERIOD_SECS[period])
    return end_time


def calc_count_from_start_and_end(start_time, end_time, period):
    rount_end_time = truncate_time_at_period(end_time, period)
    rount_start_time = truncate_time_at_period(start_time, period)
    count = int((rount_end_time - rount_start_time) / PERIOD_SECS[period])
    return count


def calc_start_from_count_and_end(count, end_time, period):
    rount_end_time = truncate_time_at_period(end_time, period)
    start_time = rount_end_time - PERIOD_SECS[period] * count
    return start_time
