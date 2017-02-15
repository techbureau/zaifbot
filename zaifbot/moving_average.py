import time
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, UTC_JP_DIFF
from zaifbot.modules.moving_average import TradeLogsManager, MovingAverageManager


def get_sma(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=int(time.time()), length=5, sma_ema='sma'):
    _get_moving_average(currency_pair, period, count, to_epoch_time, length)


def get_ema(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=int(time.time()), length=5, sma_ema='ema'):
    _get_moving_average(currency_pair, period, count, to_epoch_time, length)


def _get_moving_average(currency_pair, period, count, to_epoch_time, length):
    count = min(count, LIMIT_COUNT)
    end_time = _get_end_time(to_epoch_time, period)
    start_time = end_time - ((count + length) * PERIOD_SECS[period])

    trade_logs = TradeLogsManager(currency_pair, period)
    trade_logs.setup(start_time, end_time)

    moving_average = MovingAverageManager(currency_pair, period, length)
    moving_average.setup(start_time, end_time)


def _get_end_time(to_epoch_time, period):
    if PERIOD_SECS[period] > PERIOD_SECS['1h']:
        end_time = to_epoch_time - ((to_epoch_time + UTC_JP_DIFF) % PERIOD_SECS[period])
    else:
        end_time = to_epoch_time - (to_epoch_time % PERIOD_SECS[period])
    return end_time

