import time
from zaifbot.moving_average import get_end_time
from zaifbot.modules.bollinger_bands import BollingerBandsSetUp
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, LIMIT_LENGTH
from zaifbot.modules.dao.bollinger_bands import BollingerBandsDao


def get_bollinger_bands(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
                        to_epoch_time=None, length=LIMIT_LENGTH):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    count = min(count, LIMIT_COUNT)
    length = min(length, LIMIT_LENGTH)
    end_time = get_end_time(to_epoch_time, period)
    start_time = end_time - (count * PERIOD_SECS[period])
    bollinger_bands = BollingerBandsSetUp(currency_pair, period, count, length)

    if bollinger_bands.execute(start_time, end_time) is False:
        return {'success': 0, 'error': 'failed to set up bollinger bands'}
    return _create_return_dict(currency_pair, period, length, end_time, start_time, count)


def _create_return_dict(currency_pair, period, length, end_time, start_time, count):
    return_datas = []
    bollinger_bands = BollingerBandsDao(currency_pair, period, length)
    bollinger_bands_result = bollinger_bands.get_records(end_time, start_time, False)
    if len(bollinger_bands_result) < count:
        return {'success': 0, 'error': 'bollinger bands data is missing'}
    for i in bollinger_bands_result:
        return_datas.append({
                            'time_stamp': i.time,
                            'sd1p': i.sd1p, 'sd2p': i.sd2p, 'sd3p': i.sd3p,
                            'sd1n': i.sd1n, 'sd2n': i.sd2n, 'sd3n': i.sd3n})
    return {'success': 1, 'return': {'bollinger_bands': return_datas}}
