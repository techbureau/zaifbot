import time
import pandas as pd
from zaifbot.moving_average import get_ema


def get_macd(currency_pair, period='1d', count=5, short=12, long=26, signal=9, to_epoch_time=None):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time

    # 短期、長期のEMAを取得
    short_ema = get_ema(currency_pair, period, count + signal, to_epoch_time, short)
    long_ema = get_ema(currency_pair, period, count + signal, to_epoch_time, long)

    df_short = pd.DataFrame(short_ema['return']['ema'])
    df_long = pd.DataFrame(long_ema['return']['ema'])
    df_short.rename(columns={'moving_average': 'short_ema'}, inplace=True)
    df_long.rename(columns={'moving_average': 'long_ema'}, inplace=True)
    df = pd.merge(df_short, df_long)
    df = df[df['short_ema'] != 0.0]

    # macd = 短期EMA－長期EMA
    df['macd'] = df['short_ema'] - df['long_ema']
    df = df.reset_index(drop=True)

    # signalを求める
    zeroth_signal = df[:signal]['macd'].sum() / signal
    df['signal'] = df['macd'][-count:]
    df.ix[signal - 1] = zeroth_signal
    df['signal'] = df['signal'].ewm(span=signal, adjust=False).mean()

    # 差分を求める
    df['macd_hist'] = df['macd'] - df['signal']
    df.drop(['close', 'short_ema', 'long_ema', 'closed'], axis=1, inplace=True)

    return {'success': 1, 'return': {'macds': df[-count:].to_dict(orient='records')}}
