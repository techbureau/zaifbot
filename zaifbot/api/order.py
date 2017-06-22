import time
from uuid import uuid4
from abc import ABCMeta, abstractmethod
from threading import Thread
from zaifbot.price.stream import ZaifLastPrice
from zaifbot.api.wrapper import BotTradeApi


class OrderClient:
    def __init__(self, trade_api=None):
        self._trade_api = trade_api or BotTradeApi()
        self._active_orders = ActiveOrders()
        self._menu = _OrderMenu()

    def market_order(self, currency_pair, action, amount, comment=None):
        return self._menu.market_order(currency_pair, action, amount, comment).make_order(self._trade_api)

    def limit_order(self, currency_pair, action, limit_price, amount, comment=None):
        return self._menu.limit_order(currency_pair, action, limit_price, amount, comment).make_order(self._trade_api)

    def stop_order(self, currency_pair, action, stop_price, amount, comment=None):
        return self._menu.stop_order(currency_pair, action, stop_price, amount, comment).make_order(self._trade_api)
    #
    # def auto_cancel_by_price(self):
    #     pass
    #
    # def auto_cancel_by_time(self):
    #     pass
    #
    # def cancel(self, id=None, currency_pair=None, obj=None):
    #     pass


class _Order(metaclass=ABCMeta):
    def __init__(self):
        self._bot_order_id = str(uuid4())
        self._started_time = None

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def info(self):
        raise NotImplementedError

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

    @property
    def name(self):
        return 'MarketOrder'

    @property
    def info(self):
        info = {
            'bot_order_id': self._bot_order_id,
            'name': self.info,
            'currency_pair': self._currency_pair,
            'action': self._action,
            'price': self._round_price(),
            'started': self._started_time,
        }
        return info

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

    @property
    def name(self):
        return 'LimitOrder'

    @property
    def info(self):
        info = {
            'bot_order_id': self._bot_order_id,
            'name': self.info,
            'currency_pair': self._currency_pair,
            'action': self._action,
            'limit_price': self._limit_price,
            'started': self._started_time,
        }
        return info

    def make_order(self, trade_api):
        return trade_api.trade(currency_pair=self._currency_pair,
                               action=self._action,
                               price=self._limit_price,
                               amount=self._amount,
                               comment=self._comment)


class _OrderThread(metaclass=ABCMeta):
    def _run(self, trade_api):
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


class _StopOrder(_Order, _OrderThread):
    def __init__(self, currency_pair, action, stop_price, amount, comment=None):
        super().__init__()
        self._currency_pair = currency_pair
        self._action = action
        self._stop_price = stop_price
        self._amount = amount
        self._comment = comment

    @property
    def name(self):
        return 'StopOrder'

    @property
    def info(self):
        info = {
            'bot_order_id': self._bot_order_id,
            'name': self.info,
            'currency_pair': self._currency_pair,
            'action': self._action,
            'stop_price': self._stop_price,
            'started': self._started_time,
        }
        return info

    def make_order(self, trade_api):
        order = Thread(target=self._run, args=trade_api, daemon=True)
        order.start()

    def _execute(self, trade_api):
        return _MarketOrder(self._currency_pair, self._action, self._amount, self._comment).make_order(trade_api)

    def _can_execute(self):
        if self._action is 'bid':
            return self._is_higher_than_current_price()
        else:
            return self._is_lower_than_current_price()

    def _is_higher_than_current_price(self):
        return self._stop_price > ZaifLastPrice.last_price(self._currency_pair)

    def _is_lower_than_current_price(self):
        return self._stop_price < ZaifLastPrice.last_price(self._currency_pair)


class _OrderMenu:
    market_order = _MarketOrder
    stop_order = _StopOrder
    limit_order = _LimitOrder


class ActiveOrders:
    def add(self):
        pass

    def __init__(self):
        pass


class Observer:
    def update(self):
        pass


class OpenOrderObserver(Observer):
    pass


# class AutoCancelOrder:
#     pass
#
#
# class OrderStatus:
#     """
#     NotStarted, Active, Executed
#     """
#     pass
