from abc import ABCMeta, abstractmethod
from threading import Thread
import time
from zaifbot.price.stream import ZaifLastPrice


class Orderer:
    def __init__(self, trade_api):
        self._trade_api = trade_api
        # self._active_orders = OpenOrders()
        self._menu = _OrderMenu()

    def market_order(self, trade_api, currency_pair, action, amount, comment=None):
        self._menu.market_order(currency_pair, action, amount, comment).make_order(trade_api)

    def limit_order(self, trade_api, currency_pair, action, limit_price, amount, comment=None):
        self._menu.limit_order(currency_pair, action, limit_price, amount, comment).make_order(trade_api)

    def stop_order(self, trade_api, currency_pair, action, stop_price, amount, comment=None):
        self._menu.stop_order(currency_pair, action, stop_price, amount, comment).make_order(trade_api)

    def auto_cancel_by_price(self):
        pass

    def auto_cancel_by_time(self):
        pass

    def cancel(self, id=None, currency_pair=None, obj=None):
        pass


class _Order(metaclass=ABCMeta):
    def __init__(self):
        self._bot_order_id = None

    @abstractmethod
    def make_order(self, *args, **kwargs):
        raise NotImplementedError


class _MarketOrder(_Order):
    def __init__(self, currency_pair, action, amount, comment=None):
        super().__init__()
        self._currency_pair = currency_pair
        self._action = action
        self._amount = amount
        self._comment = comment

    def make_order(self, trade_api):
        trade_api.trade(currency_pair=self._currency_pair,
                        action=self._action,
                        price=self._round_price(),
                        amount=self._amount,
                        comment=self._comment)

    # priceの抽象化
    # todo:　中身を実装する
    def _round_price(self):
        return ZaifLastPrice.last_price(self._currency_pair)


class _LimitOrder(_Order):
    def __init__(self, currency_pair, action, limit_price, amount, comment=None):
        super().__init__()
        self._currency_pair = currency_pair
        self._action = action
        self._limit_price = limit_price
        self._amount = amount
        self._comment = comment

    def make_order(self, trade_api):
        return trade_api.trade(currency_pair=self._currency_pair,
                               action=self._action,
                               price=self._limit_price,
                               amount=self._amount,
                               comment=self._comment)


class _OrderThreadMixin(metaclass=ABCMeta):
    def run(self, trade_api):
        while True:
            if self._can_execute():
                self._execute(trade_api)
            else:
                time.sleep(1)

    @abstractmethod
    def _can_execute(self):
        raise NotImplementedError

    @abstractmethod
    def _execute(self, trade_api):
        raise NotImplementedError


class _StopOrder(_Order, _OrderThreadMixin):
    def __init__(self, currency_pair, action, stop_price, amount, comment=None):
        super().__init__()
        self._currency_pair = currency_pair
        self._action = action
        self._stop_price = stop_price
        self._amount = amount
        self._comment = comment

    def make_order(self, trade_api):
        order = Thread(target=self.run, args=trade_api, daemon=True)
        order.start()

    def _execute(self, trade_api):
        return _MarketOrder(self._currency_pair, self._action, self._amount, self._comment).make_order(trade_api)

    def _can_execute(self):
        if self._action is 'bid':
            return self._stop_price > ZaifLastPrice.last_price(self._currency_pair)
        else:
            return self._stop_price < ZaifLastPrice.last_price(self._currency_pair)


class _OrderMenu:
    market_order = _MarketOrder
    stop_order = _StopOrder
    limit_order = _LimitOrder


# class OpenOrders:
#     pass
#
#
#
# class AutoCancelOrder:
#     pass
#
#
# class OrderStatus:
#     """
#     NotStarted, Active, Executed
#     """
#     pass
