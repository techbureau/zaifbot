import time
from zaifbot.bot_common.bot_const import TRADE_ACTION
from uuid import uuid4
from abc import ABCMeta, abstractmethod
from threading import Thread
from zaifbot.price.stream import ZaifLastPrice
from zaifbot.api.wrapper import BotTradeApi


class OrderClient:
    def __init__(self, trade_api=None):
        self._trade_api = trade_api or BotTradeApi()
        self._menu = _OrderMenu()

    def market_order(self, currency_pair, action, amount, comment=None):
        return self._menu.market_order(currency_pair, action, amount, comment).make_order(self._trade_api)

    def limit_order(self, currency_pair, action, limit_price, amount, comment=None):
        return self._menu.limit_order(currency_pair, action, limit_price, amount, comment).make_order(self._trade_api)

    def stop_order(self, currency_pair, action, stop_price, amount, comment=None):
        return self._menu.stop_order(currency_pair, action, stop_price, amount, comment).make_order(self._trade_api)


class _Order(metaclass=ABCMeta):
    def __init__(self, comment):
        self._bot_order_id = str(uuid4())
        self._started_time = None
        self._comment = comment

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def info(self):
        info = {
            'bot_order_id': self._bot_order_id,
            'name': self.name,
            'started': self._started_time,
            'comment': self._comment,
        }
        return info

    @abstractmethod
    def make_order(self, *args, **kwargs):
        raise NotImplementedError


class _MarketOrder(_Order):
    def __init__(self, currency_pair, action, amount, comment=None):
        super().__init__(comment)
        self._currency_pair = currency_pair
        self._action = action
        self._amount = amount

    @property
    def name(self):
        return 'MarketOrder'

    @property
    def info(self):
        info = super().info
        info['action'] = self._action
        info['currency_pair'] = self._currency_pair
        info['price'] = self._round_price()
        info['amount'] = self._amount
        return info

    def make_order(self, trade_api):
        trade_api.trade(currency_pair=self._currency_pair,
                        action=self._action,
                        price=self._round_price(),
                        amount=self._amount,
                        comment=self._comment)

    def _round_price(self):
        # 循環参照を防ぐために現在はlast_priceを返している
        # todo: 中身の実装
        return ZaifLastPrice.last_price(self._currency_pair)


class _LimitOrder(_Order):
    def __init__(self, currency_pair, action, limit_price, amount, comment=None):
        super().__init__(comment)
        self._currency_pair = currency_pair
        self._action = action
        self._limit_price = limit_price
        self._amount = amount

    @property
    def name(self):
        return 'LimitOrder'

    @property
    def info(self):
        info = super().info
        info['currency_pair'] = self._currency_pair
        info['action'] = self._action
        info['amount'] = self._amount
        info['limit_price'] = self._limit_price
        return info

    def make_order(self, trade_api):
        return trade_api.trade(currency_pair=self._currency_pair,
                               action=self._action,
                               price=self._limit_price,
                               amount=self._amount,
                               comment=self._comment)

_SLEEP_TIME = 1


class _OrderThread(metaclass=ABCMeta):
    def _run(self, trade_api):
        while True:
            if self._can_execute():
                self._execute(trade_api)
            else:
                time.sleep(_SLEEP_TIME)

    @abstractmethod
    def _can_execute(self):
        raise NotImplementedError

    @abstractmethod
    def _execute(self, trade_api):
        raise NotImplementedError


class _StopOrder(_Order, _OrderThread):
    def __init__(self, currency_pair, action, stop_price, amount, comment=None):
        super().__init__(comment)
        self._currency_pair = currency_pair
        self._action = action
        self._stop_price = stop_price
        self._amount = amount

    @property
    def name(self):
        return 'StopOrder'

    @property
    def info(self):
        info = super().info
        info['currency_pair'] = self._currency_pair
        info['action'] = self._action
        info['amount'] = self._amount
        info['stop_price'] = self._stop_price
        return info

    def make_order(self, trade_api):
        order = Thread(target=self._run, args=trade_api, daemon=True)
        order.start()

    def _execute(self, trade_api):
        return _MarketOrder(self._currency_pair, self._action, self._amount, self._comment).make_order(trade_api)

    def _can_execute(self):
        # todo: trade_actionの抽象化
        if self._action is TRADE_ACTION[0]:
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
