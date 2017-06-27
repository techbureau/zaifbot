from wrapper import BotTradeApi

from .auto_cancel import AutoCancel
from .orders import OrderMenu


__all__ = ['Order']


class Order:
    def __init__(self, trade_api=None):
        self._api = trade_api or BotTradeApi()
        self._menu = OrderMenu()
        self._auto_cancel = AutoCancel(self._api)

    def market_order(self, currency_pair, action, amount, comment=''):
        order = self._menu.market_order(currency_pair, action, amount, comment).make_order(self._api)
        return order.info

    def limit_order(self, currency_pair, action, limit_price, amount, comment=''):
        order = self._menu.limit_order(currency_pair, action, limit_price, amount, comment).make_order(self._api)
        return order.info

    def stop_order(self, currency_pair, action, stop_price, amount, comment=''):
        order = self._menu.stop_order(currency_pair, action, stop_price, amount, comment).make_order(self._api)
        return order.info

    def time_limit_cancel(self, bot_order_id, currency_pair, wait_sec):
        return self._auto_cancel.time_limit_cancel(bot_order_id, currency_pair, wait_sec)

    def price_range_cancel(self, bot_order_id, currency_pair, target_margin):
        return self.price_range_cancel(bot_order_id, currency_pair, target_margin)
