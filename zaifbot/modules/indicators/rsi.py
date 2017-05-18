import time
from pandas import DataFrame
from zaifbot.modules.api.wrapper import BotPublicApi
import datetime

datetime.date.today() - datetime.timedelta(1)


def get_rsi(currency_pair, period, count, to_epoch_time):
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count, 'to_epoch_time': to_epoch_time}
    infos = DataFrame(public_api.everything('ohlc_data', currency_pair, second_api_params))
    return _calc_rsi(infos)


def _calc_rsi(df):
    close = df['close']
    moved_sum = 0
    increased_sum = 0
    for i in range(1, len(close)):
        moved_sum += abs(close.ix[i] - close.ix[i - 1])
        increased_sum += max(close.ix[i] - close.ix[i - 1], 0)
    return increased_sum / moved_sum * 100


if __name__ == '__main__':
    dt = datetime.date.today() - datetime.timedelta(2)
    t = time.mktime(dt.timetuple())
    info = get_rsi('btc_jpy', '1d', 5, int(t))
