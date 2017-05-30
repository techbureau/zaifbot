import time
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH, UTC_JP_DIFF
from zaifbot.modules.moving_average import TradeLogsSetUp, MovingAverageSetUp
from zaifbot.modules.dao.moving_average import MovingAverageDao, TradeLogsDao
import pandas as pd


def get_sma(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=None, length=LIMIT_LENGTH):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    return _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'sma')


def get_ema(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
            to_epoch_time=None, length=LIMIT_LENGTH):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    return _get_moving_average(currency_pair, period, count, to_epoch_time, length, 'ema')


def _get_moving_average(currency_pair, period, count, to_epoch_time, length, sma_ema):
    if to_epoch_time is None:
        to_epoch_time = int(time.time())
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
    moving_average_dao = MovingAverageDao(currency_pair, period, length)
    trade_logs_dao = TradeLogsDao(currency_pair, period)
    moving_average = \
        [i.__dict__ for i in moving_average_dao.get_records(end_time, tl_start_time, False)]
    trade_logs = \
        [i.__dict__ for i in trade_logs_dao.get_records(end_time, tl_start_time, False)]
    moving_average_df = \
        pd.DataFrame(moving_average, columns=['time', sma_ema])
    trade_logs_df = \
        pd.DataFrame(trade_logs, columns=['time', 'close', 'closed'])
    ma_result = \
        trade_logs_df.merge(moving_average_df, left_on='time', right_on='time', how='inner')
    ma_result.rename(columns={'time': 'time_stamp', sma_ema: 'moving_average'}, inplace=True)
    ma_result_length = len(ma_result.index)
    if ma_result_length == 0:
        return {'success': 0, 'error': 'moving average data is missing'}
    return_datas = ma_result[ma_result_length - length:].to_dict(orient='records')
    return {'success': 1, 'return': {sma_ema: return_datas}}
