from threading import Event

from zaifbot.order.orders.common import OrderBase, OrderThread, log_after_trade
from zaifbot.common.bot_const import Action
from zaifbot.order.orders.market_order import MarketOrder


class StopOrder(OrderBase, OrderThread):
    def __init__(self, api, currency_pair, action, stop_price, amount, comment=''):
        super(OrderThread, self).__init__(daemon=True)
        super().__init__(api, currency_pair, comment)
        self._action = Action(action)
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

    @log_after_trade('order made')
    def make_order(self):
        self.start()
        return self

    @log_after_trade('order executed')
    def _execute(self):
        return MarketOrder(self._api, self._currency_pair, self._action.value, self._amount, self._comment).make_order()

    def _can_execute(self):
        if self._action is Action.Buy:
            return self.__is_price_higher_than_stop_price()
        else:
            return self.__is_price_lower_than_stop_price()

    def __is_price_higher_than_stop_price(self):
        return self._currency_pair.last_price() > self._stop_price

    def __is_price_lower_than_stop_price(self):
        return self._currency_pair.last_price() > self._stop_price < self._stop_price

    @property
    def is_end(self):
        return self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()
