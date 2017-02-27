import time
from zaifbot.moving_average import get_sma, get_end_time
from zaifbot.modules.bollinger_bands import BollingerBandsSetUp
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT, lIMIT_LENGTH


def get_bollinger_bands(currency_pair='btc_jpy', period='1d', count=LIMIT_COUNT,
                        to_epoch_time=int(time.time()), length=lIMIT_LENGTH):
    count = min(count, LIMIT_COUNT)
    length = min(length, lIMIT_LENGTH)
    end_time = get_end_time(to_epoch_time, period)
    start_time = end_time - (count * PERIOD_SECS[period])
    bollinger_bands = BollingerBandsSetUp(currency_pair, period, count, length)
    if bollinger_bands.execute(start_time, end_time) is False:
        return 0
