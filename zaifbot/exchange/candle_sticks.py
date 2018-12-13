from zaifbot.db.dao.candle_sticks import CandleSticksDao
from zaifbot.exchange.period import Period
from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.utils.utils import int_epoch_time


class CandleSticks:
    MAX_COUNT = 1500

    def __init__(self, currency_pair, period):
        self._currency_pair = CurrencyPair(currency_pair)
        self._period = Period(period)
        self._dao = CandleSticksDao(self._currency_pair, self._period)

    def request_data(self, count=100, to_epoch_time=None):
        count = min(count, self.MAX_COUNT)
        to_epoch_time = int_epoch_time(to_epoch_time)
        end_time_rounded = self._period.truncate_sec(to_epoch_time)
        start_time = self._period.calc_start(count, end_time_rounded)

        return self._dao.get_by_duration(count, start_time, end_time_rounded)

    def last_price(self, timestamp):
        return self.request_data(count=1, to_epoch_time=timestamp)[0]['close']
