import time

from indicators.moving_average import get_end_time
from price.ohlc_prices import OhlcPrices
from talib.abstract import BBANDS
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH

__all__ = ['get_bollinger_bands']


def get_bollinger_bands(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
                        to_epoch_time=None, length=LIMIT_LENGTH, lowbd=2, upbd=2):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    count = min(count, LIMIT_COUNT)
    length = min(length, LIMIT_LENGTH)
    end_time = get_end_time(to_epoch_time, period)
    start_time = end_time - ((count + length) * PERIOD_SECS[period])
    ohlc_prices = OhlcPrices(currency_pair, period, count, length)
    ohlc_prices_result = ohlc_prices.execute(start_time, end_time)

    if len(ohlc_prices_result.index) == 0:
        return {'success': 0, 'error': 'failed to get ohlc price'}
    bbands = BBANDS(ohlc_prices_result, timeperiod=length, nbdevup=upbd, nbdevdn=lowbd, matype=0)
    ohlc_prices_result = ohlc_prices_result.merge(bbands, left_index=True, right_index=True)
    ohlc_prices_result = ohlc_prices_result[-count:][['time', 'lowerband', 'upperband']]
    return \
        {'success': 1, 'return': {'bollinger_bands': ohlc_prices_result.to_dict(orient='records')}}
