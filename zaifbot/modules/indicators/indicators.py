import pandas as pd
from pandas import DataFrame as DF
from talib import abstract as ab
from zaifbot.modules.utils import get_price_info


HIGH = 'high'
LOW = 'low'
CLOSE = 'close'
TIME = 'time'


def get_adx(currency_pair='btc_jpy', period='1d', count=100, length=14, to_epoch_time=None):
    count_needed = 2 * length - 1 + count
    df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
    adx = ab.ADX(df, timeperiod=length, prices=[HIGH, LOW, CLOSE], output_names=['adx']).rename('adx')
    adx = pd.concat([df[TIME], adx], axis=1).dropna()
    return {'success': 1, 'return': {'ADXs': adx.astype(object).to_dict(orient='records')}}


def get_macd(currency_pair='btc_jpy', period='1d', count=100, short=12, long=26, signal=9, to_epoch_time=None):
    count_needed = count + long + signal - 2
    df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
    macd = ab.MACD(df, price=CLOSE, fastperiod=short, slowperiod=long, signalperiod=signal)
    macd = pd.concat([df[TIME], macd], axis=1).dropna()
    return {'success': 1, 'return': {'MACDs':  macd.astype(object).to_dict(orient='records')}}


def get_rsi(currency_pair='btc_jpy', period='1d', count=100, length=14, to_epoch_time=None):
    count_needed = count + length
    df = DF(get_price_info(currency_pair, period, count_needed, to_epoch_time))
    rsi = ab.RSI(df, price=CLOSE, timeperiod=length).rename('rsi')
    rsi = pd.concat([df[TIME], rsi], axis=1).dropna()
    return {'success': 1, 'return': {'RSIs': rsi.astype(object).to_dict(orient='records')}}
