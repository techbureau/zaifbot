from enum import Enum


class Action(Enum):
    Buy = 'bid'
    Sell = 'ask'

# todo: 定数使わないようにする。
PERIOD_SECS = {'1d': 86400, '12h': 43200, '8h': 28800, '4h': 14400,
               '1h': 3600, '1m': 60, '5m': 300, '15m': 900, '30m': 1800}
LIMIT_COUNT = 1000
LIMIT_LENGTH = 100
UTC_JP_DIFF = 32400
