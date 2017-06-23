import time
from zaifbot.bot_common.bot_const import TRADE_ACTION
from uuid import uuid4
from abc import ABCMeta, abstractmethod
from threading import Thread, Event, Lock
from zaifbot.price.stream import ZaifLastPrice
from zaifbot.api.wrapper import BotTradeApi


# todo: calcelに対応できるようにする。

class Order:
    def __init__(self, trade_api=None):
        self._trade_api = trade_api or BotTradeApi()
        self._menu = _OrderMenu()
        self._active_orders = ActiveOrders()

    def market_order(self, currency_pair, action, amount, comment=''):
        return self._menu.market_order(currency_pair, action, amount, comment).make_order(self._trade_api)

    def limit_order(self, currency_pair, action, limit_price, amount, comment=''):
        return self._menu.limit_order(currency_pair, action, limit_price, amount, comment).make_order(self._trade_api)

    def stop_order(self, currency_pair, action, stop_price, amount, comment=''):
        return self._menu.stop_order(currency_pair, action, stop_price, amount, comment).make_order(self._trade_api)

    def active_orders(self):
        return self._active_orders.all()


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
            'comment': self._comment,
        }
        return info

    @abstractmethod
    def make_order(self, *args, **kwargs):
        raise NotImplementedError


class _MarketOrder(_Order):
    def __init__(self, currency_pair, action, amount, comment=''):
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
        return trade_api.trade(currency_pair=self._currency_pair,
                               action=self._action,
                               price=self._round_price(),
                               amount=self._amount,
                               comment=self._comment)

    def _round_price(self):
        # 丸め用の関数をimportすると循環参照してるので、現在はlast_priceを返している
        # todo: 中身の実装
        return ZaifLastPrice().last_price(self._currency_pair)['last_price']


class _LimitOrder(_Order):
    def __init__(self, currency_pair, action, limit_price, amount, comment=''):
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


class _OrderThreadRoutine(metaclass=ABCMeta):
    def _run(self, trade_api):
        while self._is_alive:
            self._every_time_before()
            if self._can_execute():
                self._before_execution()
                self._execute(trade_api)
                self._after_execution()
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
    def _is_alive(self):
        raise NotImplementedError

    def _every_time_before(self):
        pass

    def _before_execution(self):
        pass

    def _after_execution(self):
        pass


class _StopOrder(_Order, _OrderThreadRoutine):
    def __init__(self, currency_pair, action, stop_price, amount, comment=''):
        super().__init__(comment)
        self._currency_pair = currency_pair
        self._action = action
        self._stop_price = stop_price
        self._amount = amount
        self._thread = None
        self._stop_event = Event()

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
        self._thread = Thread(target=self._run, args=(trade_api,), daemon=True)
        self._thread.start()
        return self.info

    def _execute(self, trade_api):
        return _MarketOrder(self._currency_pair, self._action, self._amount, self._comment).make_order(trade_api)

    def _can_execute(self):
        if self._action is TRADE_ACTION[0]:
            return self.__is_price_higher_than_stop_price()
        else:
            return self.__is_price_lower_than_stop_price()

    def __is_price_higher_than_stop_price(self):
        return ZaifLastPrice().last_price(self._currency_pair)['last_price'] > self._stop_price

    def __is_price_lower_than_stop_price(self):
        return ZaifLastPrice().last_price(self._currency_pair)['last_price'] < self._stop_price

    @property
    def _is_alive(self):
        return self._stop_event


# もしかしたらorderを継承する可能性がある。
class _AutoCancelOrder(_OrderThreadRoutine, metaclass=ABCMeta):
    def __init__(self, target_order_id, *, is_remote=False):
        self._bot_order_id = str(uuid4())
        self._target_order_id = target_order_id
        self._is_remote = is_remote
        self._stop_event = Event()

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
            'target_order_id': self._target_order_id
        }
        return info

    @abstractmethod
    def make_order(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _can_execute(self, *args, **kwargs):
        raise NotImplementedError

    def _execute(self, order_id, trade_api):
        if self._is_remote:
            trade_api.cancel_order(order_id)
        else:
            self.__order_thread_stop(order_id)

    def __order_thread_stop(self, order_id):
        pass

    @property
    def _is_alive(self):
        return self._stop_event

    def _stop(self):
        self._stop_event.set()

    def _every_time_before(self):
        pass


class _AutoCancelByTime(_AutoCancelOrder):
    def __init__(self, target_order_id, *, is_remote=False):
        super().__init__(target_order_id, is_remote=is_remote)
        self._start_time = None
        self._wait_sec = None

    @property
    def name(self):
        return 'AutoCancelByTime'

    @property
    def info(self):
        info = super().info
        info['wait_sec'] = self._wait_sec
        info['rest_sec'] = self._wait_sec - (int(time.time()) - self._start_time)
        return info

    def make_order(self, trade_api, wait_sec):
        self._wait_sec = wait_sec
        self._start_time = int(time.time())
        order = Thread(target=self._run, args=(trade_api,), daemon=True)
        order.start()
        return self.info

    def _can_execute(self):
        return self.__is_now_the_time()

    def __is_now_the_time(self):
        return (int(time.time()) - self._start_time) >= self._wait_sec


class _AutoCancelByPrice(_AutoCancelOrder):
    def __init__(self, target_order_id, currency_pair, *, is_remote=False):
        super().__init__(target_order_id, is_remote=is_remote)
        self._currency_pair = currency_pair
        self._start_price = ZaifLastPrice().last_price(self._currency_pair)['last_price']
        self._border_margin = None

    @property
    def name(self):
        return 'AutoCancelByPrice'

    @property
    def info(self):
        info = super().info
        info['start_price'] = self._start_price
        info['border_margin'] = self._border_margin
        return info

    def make_order(self, trade_api, border_margin):
        self._border_margin = border_margin
        order = Thread(target=self._run, args=(trade_api,), daemon=True)
        order.start()
        return self.info

    def _can_execute(self):
        return self.__is_price_beyond_the_boundary()

    def __is_price_beyond_the_boundary(self):
        last_price = ZaifLastPrice().last_price(self._currency_pair)['last_price']
        return abs(self._start_price - last_price) > self._border_margin

    def _is_alive(self):
        pass


class _OrderMenu:
    market_order = _MarketOrder
    stop_order = _StopOrder
    limit_order = _LimitOrder


# observerパターンとやらを実装したら行けそう？
class ActiveOrders:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *, only_local=False):
        self._active_orders = []
        self._only_local = only_local

    def is_found(self, order_id):
        pass

    def find(self, order_id):
        return "orderオブジェクト"

    def add(self):
        pass

    def all(self):
        return self._active_orders
