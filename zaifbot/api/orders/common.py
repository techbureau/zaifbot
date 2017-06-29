from threading import Thread, Lock
from uuid import uuid4
from abc import abstractmethod, ABCMeta
from zaifbot.currency_pairs import CurrencyPair


class OrderBase(metaclass=ABCMeta):
    def __init__(self, currency_pair, comment):
        self._bot_order_id = str(BotOrderID)
        self._currency_pari = CurrencyPair(str(currency_pair))
        self._comment = comment
        self._started_time = None
        self._info = {}

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def info(self):
        self._info['bot_order_id'] = self._bot_order_id
        self._info['name'] = self.name
        self._info['comment'] = self._comment
        return self._info

    @abstractmethod
    def make_order(self, *args, **kwargs):
        raise NotImplementedError


class OrderThread(Thread):
    pass


class BotOrderID:
    order_ids = set()

    def __init__(self):
        self._id = self._gen_id()

    @classmethod
    def _gen_id(cls):
        order_id = str(uuid4())
        if order_id in cls.order_ids:
            cls._gen_id()
        return order_id

    def __str__(self):
        return self._id


class ActiveOrders:
    _instance = None
    _lock = Lock()
    _thread = Thread()
    _active_orders = {}
    _api = None

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


