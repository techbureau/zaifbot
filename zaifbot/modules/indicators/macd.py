from zaifbot.moving_average import get_ema
import time
import pandas as pd


def get_macd(currency_pair, period, count=5, short=12, long=26, signal=9, to_epoch_time=int(time.time())):
    short_ema = get_ema(currency_pair,
                        period,
                        count,
                        to_epoch_time,
                        short
                        )

    long_ema = get_ema(currency_pair,
                       period,
                       count,
                       to_epoch_time,
                       long)

    df_short = pd.DataFrame(short_ema['return']['ema'])
    df_short.rename(columns={'moving_average': 'short_ema'}, inplace=True)
    df_long = pd.DataFrame(long_ema['return']['ema'])
    df_long.rename(columns={'moving_average': 'long_ema'}, inplace=True)
    df = pd.merge(df_short, df_long)
    df = df[df['short_ema'] != 0.0]
    df = df.reset_index(drop=True)
    df['macd'] = df['short_ema'] - df['long_ema']
    df['signal'] = df['macd'].ewm(span=signal).mean()
    print(df[['macd', 'signal']])

