from zaifbot.order.orders.common import ActiveOrders
from zaifbot.wrapper import BotTradeApi

from zaifbot.order import OrderMenu


class Order:
    def __init__(self, trade_api=None):
        self._api = trade_api or BotTradeApi()
        self._menu = OrderMenu()
        self._active_orders = ActiveOrders(self._api)

    def market_order(self, currency_pair, action, amount, comment=''):
        order = self._menu.market_order(self._api, currency_pair, action, amount, comment).make_order()
        return order.info

    def limit_order(self, currency_pair, action, limit_price, amount, comment=''):
        order = self._menu.limit_order(self._api, currency_pair, action, limit_price, amount, comment).make_order()
        self._active_orders.add(order)
        return order.info

    def stop_order(self, currency_pair, action, stop_price, amount, comment=''):
        order = self._menu.stop_order(self._api, currency_pair, action, stop_price, amount, comment).make_order()
        self._active_orders.add(order)
        return order.info

    def time_limit_cancel(self, bot_order_id, currency_pair, wait_sec, comment=''):
        order = self._menu.time_limit_cancel(self._api, bot_order_id, currency_pair, wait_sec, comment).make_order()
        self._active_orders.add(order)
        return order.info

    def price_boundary_cancel(self, bot_order_id, currency_pair, target_margin):
        order = self._menu.price_boundary_cancel(self._api, bot_order_id, currency_pair, target_margin).make_order()
        self._active_orders.add(order)
        return order.info

    def active_orders(self):
        return self._active_orders.all()
