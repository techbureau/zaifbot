import pandas as pd
import pytz
from modules.indicators.bollinger_bands import get_bollinger_bands
from modules.indicators.moving_average import get_ema, get_sma
from pandas import DataFrame
from plotly.figure_factory import create_candlestick
from plotly.graph_objs import Scatter, Line, Marker
from plotly.offline import init_notebook_mode, iplot
from tzlocal import get_localzone
from zaifbot.modules.utils import get_price_info

_INCREASE = '#5959F3'
_DECREASE = '#F03030'
_SMA = '#8CAD90'
_EMA = '#DE8889'
_SIGMA1 = '#84B761'
_SIGMA2 = '#00CED1'
_SIGMA3 = '#FF7F50'


def draw_candle_chart(currency_pair, period='1d', count=20, to_epoch_time=None, **kwargs):
    fig = _candle_chart_fig(currency_pair, period, count, to_epoch_time)

    smas = kwargs.get('sma', False)
    emas = kwargs.get('ema', False)
    bands = kwargs.get('bands', False)

    if smas:
        smas = [smas] if isinstance(smas, tuple) else smas
        for sma in smas:
            fig['data'].extend([_sma_line(currency_pair, period, count, to_epoch_time, length=sma[0], color=sma[1])])
    if emas:
        emas = [emas] if isinstance(emas, tuple) else emas
        for ema in emas:
            fig['data'].extend([_ema_line(currency_pair, period, count, to_epoch_time, length=ema[0], color=ema[1])])
    if bands:
        bands = [bands] if isinstance(bands, tuple) else bands
        for band in bands:
            fig['data'].extend(_band_lines(currency_pair, period, count, to_epoch_time, length=band[0], colors=band[1]))

    iplot(fig)


def _candle_chart_fig(currency_pair, period='1d', count=20, to_epoch_time=None):
    df = DataFrame(get_price_info(currency_pair, period, count, to_epoch_time))
    df = df[['open', 'high', 'low', 'close', 'volume', 'time']]
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.set_index('time')

    # see https://github.com/plotly/plotly.py/issues/209
    df.index = df.index.tz_localize(pytz.utc).tz_convert(get_localzone()).tz_localize(None)
    init_notebook_mode(connected=True)
    decreasing = create_candlestick(df.open, df.high, df.low, df.close, dates=df.index,
                                    direction='decreasing', marker=Marker(color=_DECREASE), line=Line(color=_DECREASE))

    increasing = create_candlestick(df.open, df.high, df.low, df.close, dates=df.index,
                                    direction='increasing', marker=Marker(color=_INCREASE), line=Line(color=_INCREASE))
    fig = decreasing

    start = df.index[0]
    end = df.index[-1]

    fig['data'].extend(increasing['data'])
    fig['layout'].update({
        'title': '{} ({} ~ {})'.format(currency_pair, start, end),
        'titlefont': {'size': 18},
        'xaxis': {'showgrid': True},
        'yaxis': {'title': 'price'}
    })
    return fig


def _sma_line(currency_pair, period='1d', count=20, to_epoch_time=None, length=25, color=_SMA):
    sma = DataFrame(get_sma(currency_pair, period, count, to_epoch_time, length)['return']['sma'])
    sma = sma[sma['moving_average'] != 0]
    sma['time_stamp'] = pd.to_datetime(sma['time_stamp'], unit='s')
    sma = sma.set_index('time_stamp')
    sma.index = sma.index.tz_localize(pytz.utc).tz_convert(get_localzone()).tz_localize(None)
    sma_line = Scatter(x=sma.index, y=sma['moving_average'],
                       name='sma{}'.format(length), line=Line(color=color))
    return sma_line


def _ema_line(currency_pair, period='1d', count=20, to_epoch_time=None, length=25, color=_EMA):
    ema = DataFrame(get_ema(currency_pair, period,count, to_epoch_time, length)['return']['ema'])
    ema = ema[ema['moving_average'] != 0]
    ema['time_stamp'] = pd.to_datetime(ema['time_stamp'], unit='s')
    ema = ema.set_index('time_stamp')
    ema.index = ema.index.tz_localize(pytz.utc).tz_convert(get_localzone()).tz_localize(None)
    ema_line = Scatter(x=ema.index, y=ema['moving_average'],
                       name='ema{}'.format(length), line=Line(color=color))
    return ema_line


def _band_lines(currency_pair, period='1d', count=20, to_epoch_time=None, length=25, colors=None):
    bands = get_bollinger_bands(currency_pair, period, count, to_epoch_time, length)['return']['bollinger_bands']
    bands = DataFrame(bands)
    bands['time_stamp'] = pd.to_datetime(bands['time_stamp'], unit='s')
    bands = bands.set_index('time_stamp')
    bands.index = bands.index.tz_localize(pytz.utc).tz_convert(get_localzone()).tz_localize(None)

    if colors is None:
        colors = list()
        colors.append(_SIGMA1)
        colors.append(_SIGMA2)
        colors.append(_SIGMA3)

    l = list()
    l.append(Scatter(x=bands.index, y=bands['sd1p'], name='+1σ({})'.format(length), line=Line(color=colors[0])))
    l.append(Scatter(x=bands.index, y=bands['sd1n'], name='-1σ({})'.format(length), line=Line(color=colors[0])))
    l.append(Scatter(x=bands.index, y=bands['sd2p'], name='+2σ({})'.format(length), line=Line(color=colors[1])))
    l.append(Scatter(x=bands.index, y=bands['sd2n'], name='-2σ({})'.format(length), line=Line(color=colors[1])))
    l.append(Scatter(x=bands.index, y=bands['sd3p'], name='+3σ({})'.format(length), line=Line(color=colors[2])))
    l.append(Scatter(x=bands.index, y=bands['sd3n'], name='-3σ({})'.format(length), line=Line(color=colors[2])))
    l.append(_sma_line(currency_pair, period, count, to_epoch_time, length=length))

    return l

