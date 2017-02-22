import time
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, lIMIT_LENGTH, UTC_JP_DIFF
from zaifbot.modules.moving_average import TradeLogsSetUp, MovingAverageSetUp
from zaifbot.modules.dao.moving_average import MovingAverageDao


def get_sma(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=int(time.time()), length=lIMIT_LENGTH):
    return _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'sma')


def get_ema(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=int(time.time()), length=lIMIT_LENGTH):
    return _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'ema')


def _get_moving_average(currency_pair, period, count, to_epoch_time, length, sma_ema):
    count = min(count, LIMIT_COUNT)
    length = min(length, lIMIT_LENGTH)
    end_time = _get_end_time(to_epoch_time, period)
    tl_start_time = end_time - ((count + length) * PERIOD_SECS[period])
    ma_start_time = end_time - (count * PERIOD_SECS[period])

    trade_logs = TradeLogsSetUp(currency_pair, period, count, length)
    if trade_logs.execute(tl_start_time, end_time) is False:
        return {'success': 0, 'error': 'failed to set up trade log'}

    moving_average = MovingAverageSetUp(currency_pair, period, count, length)
    ma_result = moving_average.execute(ma_start_time, tl_start_time, end_time)
    if ma_result is False:
        return {'success': 0, 'error': 'failed to set up trade log'}
    return _create_return_dict(sma_ema, currency_pair, period, length, end_time, ma_start_time)


def _get_end_time(to_epoch_time, period):
    if PERIOD_SECS[period] > PERIOD_SECS['1h']:
        end_time = to_epoch_time - ((to_epoch_time + UTC_JP_DIFF) % PERIOD_SECS[period])
    else:
        end_time = to_epoch_time - (to_epoch_time % PERIOD_SECS[period])
    return end_time


def _create_return_dict(sma_ema, currency_pair, period, length, end_time, ma_start_time):
    return_ = []
    moving_average = MovingAverageDao(currency_pair, period, length)
    ma_result = moving_average.get_records(end_time, ma_start_time)
    for i in ma_result:
        if sma_ema == 'sma':
            moving_average = i.sma
        elif sma_ema == 'ema':
            moving_average = i.ema
        return_.append({'time_stamp': i.time, 'value': moving_average})
    return {'success': 1, 'return': {sma_ema: return_}}
