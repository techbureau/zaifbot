from zaifbot.exchange.action import Action
from zaifbot.utils import datetime2timestamp
from zaifbot.exchange.period import Period
from zaifbot.indicators.candle_sticks import CandleSticks
from pandas import DataFrame
from zaifbot.logger import trade_logger


class BTRule:
    pass


class BTEntry(BTRule):
    def __init__(self, amount, action='bid'):
        self._currency_pair = None
        self._amount = amount
        self._action = Action(action)

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self, time, price):
        trade_logger.info('time: {}, price: {}'.format(time, price))


class BTExit(BTRule):
    def can_exit(self):
        raise NotImplementedError

    def exit(self, time, price):
        trade_logger.info('time: {}, price: {}'.format(time, price))


class BTContext:
    def __init__(self, from_datetime, to_datetime, *, period='1m'):
        self._from_time = datetime2timestamp(from_datetime)
        self._to_time = datetime2timestamp(to_datetime)
        self._period = Period(period)
        # 1度目のupdateで0にしたいから
        self._index = -1
        self._times = []
        self._prices = []
        self._size = None
        self._is_continue = True

    def current_time(self):
        return self._times[self._index]

    def current_price(self):
        return self._prices[self._index]

    def update(self):
        if self._index >= self._size - 1:
            self.stop()
        else:
            self._index += 1

    @property
    def is_continue(self):
        return self._is_continue

    def stop(self):
        self._is_continue = False

    def setup_data(self, currency_pair):
        candle_sticks = CandleSticks(currency_pair, self._period)
        count = self._get_data_count()
        data = DataFrame(candle_sticks.request_data(count, self._to_time))['close', 'time']
        self._times = data['time']
        self._prices = data['close']
        self._size = len(data)

    def _get_data_count(self):
        return self._period.calc_count(self._from_time, self._to_time)
