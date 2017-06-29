import time
from zaifbot.bot_common.bot_const import TRADE_ACTION
from abc import ABCMeta, abstractmethod
from threading import Thread, Event
from zaifbot.currency_pairs import CurrencyPair


class _LimitOrder(_Order):
    def __init__(self, currency_pair, action, limit_price, amount, comment=''):
        super().__init__(comment)
        self._currency_pair = CurrencyPair(currency_pair)
        self._action = action
        self._limit_price = limit_price
        self._amount = amount

    @property
    def name(self):
        return 'LimitOrder'

    @property
    def info(self):
        self._info = super().info
        self._info['currency_pair'] = str(self._currency_pair)
        self._info['action'] = self._action
        self._info['amount'] = self._amount
        self._info['limit_price'] = self._limit_price
        return self._info

    def make_order(self, trade_api):
        result = trade_api.trade(currency_pair=str(self._currency_pair),
                                 action=self._action,
                                 price=self._limit_price,
                                 amount=self._amount,
                                 comment=self._comment)
        self._info['zaif_order_id'] = result['order_id']
        return self


_SLEEP_TIME = 1


class _OrderThreadRoutine(metaclass=ABCMeta):
    def _run(self, trade_api):
        while self.is_alive:
            self._every_time_before()
            if self._can_execute():
                self._before_execution()
                self._execute(trade_api)
                self._after_execution()
                self.stop()
            else:
                time.sleep(_SLEEP_TIME)

    @abstractmethod
    def _can_execute(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _execute(self, *args, **kwargs):
        raise NotImplementedError

    @property
    @abstractmethod
    def is_alive(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    def _every_time_before(self):
        pass

    def _before_execution(self):
        pass

    def _after_execution(self):
        pass





class OrderMenu:
    market_order = _MarketOrder
    stop_order = _StopOrder
    limit_order = _LimitOrder