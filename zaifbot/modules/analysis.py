import time
import pandas as pd
from pandas import DataFrame
from zaifbot.modules.utils import get_price_info
from plotly.offline import init_notebook_mode, iplot
from plotly.figure_factory import create_candlestick


def draw_candle_chart(currency_pair, period='1d', count=20, to_epoch_time=None):
    fig = _get_candle_chart_fig(currency_pair, period, count, to_epoch_time)
    iplot(fig)


def _get_candle_chart_fig(currency_pair, period='1d', count=20, to_epoch_time=None):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time

    # データの取得
    df = DataFrame(get_price_info(currency_pair, period, count, to_epoch_time))
    df = df[['open', 'high', 'low', 'close', 'volume', 'time']]
    df['time'] = pd.to_datetime(df['time'], unit='s')
    init_notebook_mode(connected=True)
    fig = create_candlestick(df.open, df.high, df.low, df.close, dates=df.time)
    fig['layout'].update({
        'xaxis': {
            'showgrid': True
        }
    })
    return fig

