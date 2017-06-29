from threading import Thread, Lock, Event
import time
from uuid import uuid4
from abc import abstractmethod, ABCMeta
from zaifbot.currency_pairs import CurrencyPair


class OrderBase(metaclass=ABCMeta):
    def __init__(self, api, currency_pair, comment):
        self._api = api
        self._bot_order_id = str(BotOrderID())
        self._currency_pair = CurrencyPair(currency_pair)
        self._comment = comment
        self._started_time = None
        self._info = {}

    @property
    @abstractmethod
    def type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def info(self):
        self._info['bot_order_id'] = self._bot_order_id
        self._info['type'] = self.type
        self._info['currency_pair'] = self._currency_pair
        self._info['comment'] = self._comment
        return self._info

    @abstractmethod
    def make_order(self, *args, **kwargs):
        raise NotImplementedError


class OrderThread(Thread, metaclass=ABCMeta):

    def run(self):
        while self._is_end:
            self._every_time_before()
            if self._can_execute():
                self._before_execution()
                self._execute()
                self._after_execution()
                self.stop()
            else:
                time.sleep(1)

    @abstractmethod
    def _can_execute(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _execute(self, *args, **kwargs):
        raise NotImplementedError

    @property
    @abstractmethod
    def _is_end(self):
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


class BotOrderID:
    order_ids = set()
    _lock = Lock()

    def __init__(self):
        self._id = self._gen_id()

    @classmethod
    def _gen_id(cls):
        order_id = str(uuid4())
        with cls._lock:
            if order_id not in cls.order_ids:
                return order_id
        cls._gen_id()

    def __str__(self):
        return self._id


class ActiveOrders:
    _instance = None
    _api = None
    _lock = Lock()
    _thread = Thread()
    _active_orders = {}

    def __new__(cls, api):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._api = api
        return cls._instance

    def find(self, bot_order_id):
        return self._active_orders.get(bot_order_id, None)

    def add(self, order):
        with self._lock:
            bot_order_id = order.info['bot_order_id']
            self._active_orders[bot_order_id] = order

    def remove(self, bot_order_id):
        self._active_orders.pop(bot_order_id)

    def all(self):
        return self._active_orders

    def update(self):
        with self._lock:
            remote_order_ids = self._fetch_remote_order_ids()
            for active_order in self._active_orders:
                if active_order.info.get('zaif_order_id') not in remote_order_ids:
                    self._active_orders.pop(active_order.info.bot_order_id)
            for active_order in self._active_orders:
                if active_order.is_alive is False:
                    self._active_orders.pop(active_order.info.bot_order_id)

    @classmethod
    def _fetch_remote_order_ids(cls):
        orders = cls._api.active_orders(is_token_both=True)
        return orders['token_active_orders'].keys() + orders['active_orders'].keys()


class AutoCancelOrder(OrderBase, OrderThread):
    def __init__(self, trade_api, target_bot_order_id, currency_pair, comment=''):
        super().__init__(trade_api, currency_pair, comment)
        super(OrderThread, self).__init__(daemon=True)
        self._target_bot_order_id = target_bot_order_id
        self._active_orders = ActiveOrders(trade_api)
        self._stop_event = Event()

    @property
    def type(self):
        raise NotImplementedError

    @property
    def info(self):
        info = super().info
        info['target_bot_orderr_id'] = self._target_bot_order_id
        return info

    def make_order(self):
        raise NotImplementedError

    def _execute(self):
        # 未実装
        self._api.cancel_order(order_id=self._target_bot_order_id, is_token=self._currency_pair.is_token())
        self.stop()

    def _can_execute(self):
        raise NotImplementedError

    def stop(self):
        self._stop_event.set()

    def _is_end(self):
        return self._stop_event.is_set()

    def _every_time_before(self):
        print('a')

