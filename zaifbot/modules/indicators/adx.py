import time
import pandas as pd
from pandas import DataFrame, Series
from zaifbot.modules.api.wrapper import BotPublicApi


def get_adx(currency_pair, period='1d', count=5, length=14, to_epoch_time=None):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count + 2 * length - 1, 'to_epoch_time': to_epoch_time}
    price_infos = DataFrame(public_api.everything('ohlc_data', currency_pair, second_api_params))
    return _get_adx(price_infos[['high', 'low', 'time', 'close']].copy(), length, count)


def _get_adx(df, length, count):
    def _create_dict(df, count):
        adxs = df.ix[len(df) - count:, ['time', 'ADX']].to_dict(orient='records')
        return {'success': 1, 'return': {'adxs': adxs}}

    df = pd.concat([df, _get_dm(df)], axis=1)
    df['TR'] = _get_tr(df)
    df = _get_di(df, length, count)
    df['DX'] = abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']) * 100
    df = _calc_adx(df, length, count)
    return _create_dict(df, count)


def _get_dm(df):
    """引数にはhigh,low, closeをカラム名に持つDataFrameをとる"""
    def _calc_dm(row):
        high_dff = max(row['high'], 0)
        low_diff = min(row['low'], 0)

        if abs(high_dff) > abs(low_diff):
            return Series({'+DM': high_dff, '-DM': 0})
        elif abs(high_dff) < abs(low_diff):
            return Series({'+DM': 0, '-DM': abs(low_diff)})
        else:
            return Series({'+DM': 0, '-DM': 0})

    return df.diff().fillna(0).apply(_calc_dm, axis=1)


def _get_tr(df):
    """引数にはhigh, low, closeをカラム名に持つDataFrameをとる"""
    new_row = [0]
    for i in range(1, len(df)):
        tdy_high_minus_ystday_high = df.ix[i, 'high'] - df.ix[i, 'low']
        tdy_high_minus_ystday_close = abs(df.ix[i, 'high'] - df.ix[i - 1, 'close'])
        ystday_close_minus_tdy_low = abs(df.ix[i - 1, 'close'] - df.ix[i, 'low'])
        new_row.append(max(tdy_high_minus_ystday_high, tdy_high_minus_ystday_close, ystday_close_minus_tdy_low))
    return new_row


def _get_di(df, length, count):
    # 最初のDI
    df.ix[length, '+DM14'] = df.ix[1:length, '+DM'].sum()
    df.ix[length, '-DM14'] = df.ix[1:length, '-DM'].sum()
    df.ix[length, 'TR14'] = df.ix[1:length, 'TR'].sum()

    df.ix[length, '+DI'] = df.ix[length, '+DM14'] / df.ix[length, 'TR14'] * 100
    df.ix[length, '-DI'] = df.ix[length, '-DM14'] / df.ix[length, 'TR14'] * 100

    # 2つ目以降のDI
    for i in range(length + 1, count + length * 2 - 1):
        df.ix[i, '+DM14'] = df.ix[i - 1, '+DM14'] * (length - 1) / length + df.ix[i, '+DM']
        df.ix[i, '-DM14'] = df.ix[i - 1, '-DM14'] * (length - 1) / length + df.ix[i, '-DM']
        df.ix[i, 'TR14'] = df.ix[i - 1, 'TR14'] * (length - 1) / length + df.ix[i, 'TR']

        df.ix[i, '+DI'] = df.ix[i, '+DM14'] / df.ix[i, 'TR14'] * 100
        df.ix[i, '-DI'] = df.ix[i, '-DM14'] / df.ix[i, 'TR14'] * 100
    return df.fillna(0)


def _calc_adx(df, length, count):
    # 1本目のadx
    df.ix[len(df) - count, 'ADX'] = df.ix[length:len(df) - count, 'DX'].sum()
    for i in range(len(df) - count + 1, len(df)):
        df.ix[i, 'ADX'] = (df.ix[i - 1, 'ADX'] * (length - 1) + df.ix[i, 'DX']) / 14
    return df.fillna(0)