import time
from uuid import uuid4
from threading import Thread, Lock, Event
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
        self._info['currency_pair'] = str(self._currency_pair)
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
    _orders_lock = Lock()

    def __new__(cls, api):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._api = api
        return cls._instance

    def find(self, bot_order_id):
        with self._orders_lock:
            return self._active_orders.get(bot_order_id, None)

    def add(self, order):
        with self._orders_lock:
            bot_order_id = order.info['bot_order_id']
            self._active_orders[bot_order_id] = order

    def remove(self, bot_order_id):
        with self._orders_lock:
            self._active_orders.pop(bot_order_id)

    def all(self):
        with self._orders_lock:
            # change if better way founded
            remote_orders = filter(lambda x: x.info.get('zaif_order_id', None), set(self._active_orders.values()))
            threads_orders = filter(lambda x: not x.info.get('zaif_order_id', None), set(self._active_orders.values()))

            for remote_order in remote_orders:
                ids_from_server = self._fetch_remote_order_ids()
                if remote_order.info['zaif_order_id'] not in ids_from_server:
                    self._active_orders.pop(remote_order.info['bot_order_id'])

            for threads_order in threads_orders:
                if threads_order.is_end:
                    self._active_orders.pop(threads_order.info['bot_order_id'])
        return self._active_orders

    @classmethod
    def _fetch_remote_order_ids(cls):
        orders = cls._api.active_orders(is_token_both=True)
        return list(orders['token_active_orders'].keys()) + list(orders['active_orders'].keys())


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
        info['target_bot_order_id'] = self._target_bot_order_id
        return info

    def make_order(self):
        raise NotImplementedError

    def _execute(self):
        target = self._active_orders.find(self._target_bot_order_id)
        if target.info.get('zaif_order_id', None):
            self._api.cancel_order(order_id=self._target_bot_order_id,
                                   is_token=self._currency_pair.is_token())
        else:
            target.stop()

    def _can_execute(self):
        raise NotImplementedError

    def stop(self):
        self._stop_event.set()

    def _is_end(self):
        return self._stop_event.is_set()

    def _every_time_before(self):
        if self.info['target_bot_order_id'] not in self._active_orders.all():
            self.stop()
