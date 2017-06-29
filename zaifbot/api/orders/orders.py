import time
from zaifbot.bot_common.bot_const import TRADE_ACTION
from abc import ABCMeta, abstractmethod
from threading import Thread, Event
from zaifbot.currency_pairs import CurrencyPair




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