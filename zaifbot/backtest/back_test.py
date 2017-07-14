from zaifbot.trade_strategy import Strategy
from zaifbot.logger import trade_logger
from zaifbot.utils import datetime2timestamp
from zaifbot.exchange.period import Period


class BackTest(Strategy):
    def __init__(self, from_datetime, to_datetime, currency_pair, period, entry_rule, exit_rule, stop_rule=None):
        self._from_time = datetime2timestamp(from_datetime)
        self._to_time = datetime2timestamp(to_datetime)
        self._period = Period(period)
        self._index = -1 #初回のupdateで1にしたい
        self._size = self._period.calc_count(self._from_time, self._to_time)
        super().__init__(currency_pair, entry_rule, exit_rule, stop_rule)

    def start(self, **kwargs):
        super().start(sec_wait=0)

    def _entry(self):
        pass

    def _exit(self):
        pass

    def regular_job(self):
        self._update_time()

    def _update_time(self):
        if self._index >= self._size:
            self.stop()
        else:
            self._index += 1
