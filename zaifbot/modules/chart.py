import pandas as pd
from pandas import DataFrame
from plotly.offline import init_notebook_mode, iplot
from plotly.figure_factory import create_candlestick
from plotly.graph_objs import Scatter, Line, Marker
from zaifbot.modules.utils import get_price_info
from zaifbot.moving_average import get_ema, get_sma
from zaifbot.bollinger_bands import get_bollinger_bands


INCREASE = '#5959F3'
DECREASE = '#F03030'
SMA = '#8CAD90'
EMA = '#DE8889'
SIGMA1 = '#84B761'
SIGMA2 = '#00CED1'
SIGMA3 = '#FF7F50'


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
    init_notebook_mode(connected=True)
    decreasing = create_candlestick(df.open, df.high, df.low, df.close, dates=df.time,
                                    direction='decreasing', marker=Marker(color=DECREASE), line=Line(color=DECREASE))

    increasing = create_candlestick(df.open, df.high, df.low, df.close, dates=df.time,
                                    direction='increasing', marker=Marker(color=INCREASE), line=Line(color=INCREASE))
    fig = decreasing
    fig['data'].extend(increasing['data'])
    fig['layout'].update({
        'xaxis': { 'showgrid': True }
    })
    return fig


def _sma_line(currency_pair, period='1d', count=20, to_epoch_time=None, length=25, color=SMA):
    sma = DataFrame(get_sma(currency_pair, period, count, to_epoch_time, length)['return']['sma'])
    sma = sma[sma['moving_average'] != 0]
    sma['time_stamp'] = pd.to_datetime(sma['time_stamp'], unit='s')
    sma_line = Scatter(x=sma['time_stamp'], y=sma['moving_average'],
                       name='sma{}'.format(length), line=Line(color=color))
    return sma_line


def _ema_line(currency_pair, period='1d', count=20, to_epoch_time=None, length=25, color=EMA):
    ema = DataFrame(get_ema(currency_pair, period,count, to_epoch_time, length)['return']['ema'])
    ema = ema[ema['moving_average'] != 0]
    ema['time_stamp'] = pd.to_datetime(ema['time_stamp'], unit='s')
    ema_line = Scatter(x=ema['time_stamp'], y=ema['moving_average'],
                       name='ema{}'.format(length), line=Line(color=color))
    return ema_line


def _band_lines(currency_pair, period='1d', count=20, to_epoch_time=None, length=25, colors=None):
    bands = get_bollinger_bands(currency_pair, period, count, to_epoch_time, length)['return']['bollinger_bands']
    bands = DataFrame(bands)
    bands['time_stamp'] = pd.to_datetime(bands['time_stamp'], unit='s')

    if colors is None:
        colors = list()
        colors.append(SIGMA1)
        colors.append(SIGMA2)
        colors.append(SIGMA3)

    l = list()
    l.append(Scatter(x=bands['time_stamp'], y=bands['sd1p'], name='+1σ({})'.format(length), line=Line(color=colors[0])))
    l.append(Scatter(x=bands['time_stamp'], y=bands['sd1n'], name='-1σ({})'.format(length), line=Line(color=colors[0])))
    l.append(Scatter(x=bands['time_stamp'], y=bands['sd2p'], name='+2σ({})'.format(length), line=Line(color=colors[1])))
    l.append(Scatter(x=bands['time_stamp'], y=bands['sd2n'], name='-2σ({})'.format(length), line=Line(color=colors[1])))
    l.append(Scatter(x=bands['time_stamp'], y=bands['sd3p'], name='+3σ({})'.format(length), line=Line(color=colors[2])))
    l.append(Scatter(x=bands['time_stamp'], y=bands['sd3n'], name='-3σ({})'.format(length), line=Line(color=colors[2])))
    l.append(_sma_line(currency_pair, period, count, to_epoch_time, length=25))

    return l

