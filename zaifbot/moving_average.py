import time
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH, UTC_JP_DIFF
from zaifbot.modules.moving_average import TradeLogsSetUp, MovingAverageSetUp
from zaifbot.modules.dao.moving_average import MovingAverageDao


def get_sma(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=int(time.time()), length=LIMIT_LENGTH):
    return _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'sma')


def get_ema(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=int(time.time()), length=LIMIT_LENGTH):
    return _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'ema')


def _get_moving_average(currency_pair, period, count, to_epoch_time, length, sma_ema):
    count = min(count, LIMIT_COUNT)
    length = min(length, LIMIT_LENGTH)
    end_time = get_end_time(to_epoch_time, period)
    tl_start_time = end_time - ((count + length) * PERIOD_SECS[period])
    ma_start_time = end_time - (count * PERIOD_SECS[period])

    trade_logs = TradeLogsSetUp(currency_pair, period, count, length)
    if trade_logs.execute(tl_start_time, end_time) is False:
        return {'success': 0, 'error': 'failed to set up trade log'}

    moving_average = MovingAverageSetUp(currency_pair, period, count, length)
    ma_result = moving_average.execute(ma_start_time, tl_start_time, end_time)
    if ma_result is False:
        return {'success': 0, 'error': 'failed to set up moving average'}
    return _create_return_dict(sma_ema, currency_pair, period,
                               length, end_time, tl_start_time, count)


def get_end_time(to_epoch_time, period):
    if PERIOD_SECS[period] > PERIOD_SECS['1h']:
        end_time = to_epoch_time - ((to_epoch_time + UTC_JP_DIFF) % PERIOD_SECS[period])
    else:
        end_time = to_epoch_time - (to_epoch_time % PERIOD_SECS[period])
    return end_time


def _create_return_dict(sma_ema, currency_pair, period, length, end_time, tl_start_time, count):
    return_datas = []
    moving_average = MovingAverageDao(currency_pair, period, length)
    ma_result = moving_average.get_trade_logs_moving_average(end_time, tl_start_time)
    if len(ma_result) < count:
        return {'success': 0, 'error': 'moving average data is missing'}
    for i in ma_result:
        if sma_ema == 'sma' and i.MovingAverages:
            moving_average = i.MovingAverages.sma
        elif sma_ema == 'ema' and i.MovingAverages:
            moving_average = i.MovingAverages.ema
        else:
            moving_average = 0.0
        return_datas.append({'time_stamp': i.TradeLogs.time, 'moving_average': moving_average,
                             'close': i.TradeLogs.close, 'closed': bool(i.TradeLogs.closed)})
    return {'success': 1, 'return': {sma_ema: return_datas}}
