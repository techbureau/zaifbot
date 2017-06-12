import traceback

import pandas as pd
from pandas import DataFrame as DF
from talib import abstract as ab
from utils import get_price_info
from zaifbot.bot_common.logger import logger

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'


__all__ = ['get_adx', 'get_rsi', 'get_macd']


def get_adx(currency_pair='btc_jpy', period='1d', count=100, length=14, to_epoch_time=None):
    try:
        count_needed = 2 * length - 1 + count
        df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
        adx = ab.ADX(df, timeperiod=length, prices=[_HIGH, _LOW, _CLOSE], output_names=['adx']).rename('adx')
        adx = pd.concat([df[_TIME], adx], axis=1).dropna()
        return {'success': 1, 'return': {'ADXs': adx.astype(object).to_dict(orient='records')}}
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'success': 0, 'error': e}


def get_macd(currency_pair='btc_jpy', period='1d', count=100, short=12, long=26, signal=9, to_epoch_time=None):
    try:
        count_needed = count + long + signal - 2
        df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
        macd = ab.MACD(df, price=_CLOSE, fastperiod=short, slowperiod=long, signalperiod=signal)
        macd = pd.concat([df[_TIME], macd], axis=1).dropna()
        return {'success': 1, 'return': {'MACDs':  macd.astype(object).to_dict(orient='records')}}
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'success': 0, 'error': e}


def get_rsi(currency_pair='btc_jpy', period='1d', count=100, length=14, to_epoch_time=None):
    try:
        count_needed = count + length
        df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
        rsi = ab.RSI(df, price=_CLOSE, timeperiod=length).rename('rsi')
        rsi = pd.concat([df[_TIME], rsi], axis=1).dropna()
        return {'success': 1, 'return': {'RSIs': rsi.astype(object).to_dict(orient='records')}}
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return {'success': 0, 'error': e}
