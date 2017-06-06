import time
from zaifbot.moving_average import get_end_time
from zaifbot.modules.trade_logs import TradeLogs
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH
from talib.abstract import BBANDS


def get_bollinger_bands(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
                        to_epoch_time=None, length=LIMIT_LENGTH, lowbd=2, upbd=2):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    count = min(count, LIMIT_COUNT)
    length = min(length, LIMIT_LENGTH)
    end_time = get_end_time(to_epoch_time, period)
    start_time = end_time - ((count + length) * PERIOD_SECS[period])
    trade_logs = TradeLogs(currency_pair, period, count, length)
    trade_logs_result = trade_logs.execute(start_time, end_time)

    if len(trade_logs_result.index) == 0:
        return {'success': 0, 'error': 'failed to get trade log'}
    bbands = BBANDS(trade_logs_result, timeperiod=length, nbdevup=upbd, nbdevdn=lowbd, matype=0)
    trade_logs_result = trade_logs_result.merge(bbands, left_index=True, right_index=True)
    trade_logs_result = trade_logs_result[-count:][['time', 'lowerband', 'upperband']]
    return \
        {'success': 1, 'return': {'bollinger_bands': trade_logs_result.to_dict(orient='records')}}
