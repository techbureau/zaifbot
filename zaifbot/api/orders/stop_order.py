from threading import Event
from zaifbot.bot_common.bot_const import TRADE_ACTION
from zaifbot.api.orders.common import OrderBase, OrderThread
from zaifbot.api.orders.market_order import MarketOrder


class StopOrder(OrderBase, OrderThread):
    def __init__(self, api, currency_pair, action, stop_price, amount, comment=''):
        super(OrderThread, self).__init__(daemon=True)
        super().__init__(api, currency_pair, comment)
        self._action = action
        self._stop_price = stop_price
        self._amount = amount
        self._stop_event = Event()

    @property
    def type(self):
        return 'StopOrder'

    @property
    def info(self):
        self._info = super().info
        self._info['action'] = self._action
        self._info['amount'] = self._amount
        self._info['stop_price'] = self._stop_price
        return self._info

    def make_order(self):
        self.start()
        return self

    def _execute(self):
        return MarketOrder(self._api, self._currency_pair, self._action, self._amount, self._comment).make_order()

    def _can_execute(self):
        if self._action is TRADE_ACTION[0]:
            return self.__is_price_higher_than_stop_price()
        else:
            return self.__is_price_lower_than_stop_price()

    def __is_price_higher_than_stop_price(self):
        return self._currency_pair.last_price()['last_price'] > self._stop_price

    def __is_price_lower_than_stop_price(self):
        return self._currency_pair.last_price()['last_price'] > self._stop_price < self._stop_price

    @property
    def _is_end(self):
        return not self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()
