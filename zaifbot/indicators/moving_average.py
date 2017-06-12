import time

from ohlc_prices import OhlcPrices
from talib.abstract import SMA, EMA
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH, UTC_JP_DIFF


def get_sma(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=None, length=LIMIT_LENGTH):
    moving_average = _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'sma')
    return moving_average


def get_ema(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=None, length=LIMIT_LENGTH):
    moving_average = _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'ema')
    return moving_average


def _get_moving_average(currency_pair, period, count, to_epoch_time, length, sma_ema):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    count = min(count, LIMIT_COUNT)
    length = min(length, LIMIT_LENGTH)
    end_time = get_end_time(to_epoch_time, period)
    tl_start_time = end_time - ((count + length) * PERIOD_SECS[period])
    ohlc_prices = OhlcPrices(currency_pair, period, count, length)
    ohlc_prices_result = ohlc_prices.execute(tl_start_time, end_time)

    if len(ohlc_prices_result.index) == 0:
        return {'success': 0, 'error': 'failed to get ohlc prices'}
    sma = SMA(ohlc_prices_result, timeperiod=length)
    ema = EMA(ohlc_prices_result, timeperiod=length)
    ohlc_prices_result = \
        ohlc_prices_result.merge(sma.to_frame(), left_index=True, right_index=True)\
        .rename(columns={0: 'sma'})
    ohlc_prices_result = \
        ohlc_prices_result.merge(ema.to_frame(), left_index=True, right_index=True)\
        .rename(columns={0: 'ema'})
    if sma_ema == 'sma':
        ohlc_prices_result = ohlc_prices_result[-count:].drop('ema', axis=1)\
            .rename(columns={sma_ema: 'moving_average'}).to_dict(orient='records')
    else:
        ohlc_prices_result = ohlc_prices_result[-count:].drop('ema', axis=1)\
            .rename(columns={sma_ema: 'moving_average'}).to_dict(orient='records')
    return {'success': 1, 'return': {sma_ema: ohlc_prices_result}}


def get_end_time(to_epoch_time, period):
    if PERIOD_SECS[period] > PERIOD_SECS['1h']:
        end_time = to_epoch_time - ((to_epoch_time + UTC_JP_DIFF) % PERIOD_SECS[period])
    else:
        end_time = to_epoch_time - (to_epoch_time % PERIOD_SECS[period])
    return end_time
