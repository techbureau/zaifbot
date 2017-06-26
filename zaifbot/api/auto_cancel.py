import time
from abc import ABCMeta, abstractmethod
from threading import Thread, Event, Lock
from uuid import uuid4
from zaifbot.bot_common.errors import ZaifBotError
from zaifbot.price.cache import ZaifCurrencyPairs
from zaifbot.price.utils import get_current_last_price


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


class AutoCancel:
    def __init__(self, trade_api):
        self._auto_cancel_orders = {}
        self._trade_api = trade_api
        self._active_orders = ActiveOrders(self._trade_api)

    def time_limit_cancel(self, bot_order_id, currency_pair, wait_sec):
        auto_cancel = _AutoCancelByTime(self._trade_api, bot_order_id, currency_pair, wait_sec)
        auto_cancel.start()
        self._active_orders.add(auto_cancel)
        return auto_cancel.info

    def price_range_cancel(self, bot_order_id, currency_pair, target_margin):
        auto_cancel = _AutoCancelByPrice(self._trade_api, bot_order_id, currency_pair, target_margin)
        auto_cancel.start()
        self._active_orders.add(auto_cancel)
        return auto_cancel.info

_SLEEP_TIME = 1


class _AutoCancelOrder(Thread, metaclass=ABCMeta):
    def __init__(self, trade_api, target_bot_order_id, currency_pair):
        super().__init__(daemon=True)
        self._api = trade_api
        self._bot_order_id = BotOrderID()
        self._target_bot_order_id = target_bot_order_id
        self._currency_pair = currency_pair
        self._is_token = self._is_token(currency_pair)
        self._stop_event = Event()
        self._start_time = None

    def run(self):
        self._start_time = time.time()
        while self._stop_event.is_set() is False:
            active_orders = self._api.active_orders(currency_pair=self._currency_pair)
            if str(self._bot_order_id) not in active_orders:
                self.stop()
                continue
            if self._can_execute():
                self._execute()
            else:
                time.sleep(_SLEEP_TIME)

    @property
    def info(self):
        info = {
            'bot_order_id': self._bot_order_id,
            'name': self.name,
            'target_bot_order_id': self._target_bot_order_id,
            'currency_pair': self._currency_pair,
            'is_token': self._is_token,
            'started': self._start_time,
        }
        return info

    def _execute(self):
        self._api.cancel_order(order_id=self._target_bot_order_id, is_token=self._is_token)
        self.stop()

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def _is_token(currency_pair):
        currency_pairs = ZaifCurrencyPairs()
        record = currency_pairs[currency_pair]
        if record:
            return record['is_token']
        raise ZaifBotError('illegal currency_pair:{}'.format(currency_pair))

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @abstractmethod
    def _can_execute(self):
        raise NotImplementedError


class _AutoCancelByTime(_AutoCancelOrder):
    def __init__(self, trade_api, order_id, currency_pair, wait_sec):
        super().__init__(trade_api, order_id, currency_pair)
        self._wait_sec = wait_sec

    @property
    def info(self):
        info = super().info
        info['wait_sec'] = self._wait_sec
        info['rest_time'] = self._wait_sec - (time.time() - self._start_time)
        return info

    def _can_execute(self):
        if time.time() - self._start_time < self._wait_sec:
            return False
        return True

    @property
    def name(self):
        return 'TimeLimitCancel'


class _AutoCancelByPrice(_AutoCancelOrder):
    def __init__(self, trade_api, order_id, currency_pair, target_margin):
        super().__init__(trade_api, order_id, currency_pair)
        self._target_margin = target_margin
        self._currency_pair = currency_pair
        self._start_price = None

    @property
    def info(self):
        info = super().info
        info['start_price'] = self._start_price
        info['target_margin'] = self._target_margin
        info['current_margin'] = abs(info['current_price'] - self._start_price)
        return info

    def run(self):
        self._start_price = get_current_last_price(self._currency_pair)['last_price']
        super().run()

    def _can_execute(self):
        last_price = get_current_last_price(self._currency_pair)['last_price']
        if abs(self._start_price - last_price) < self._target_margin:
            return False
        return True

    @property
    def name(self):
        return 'PriceRangeCancel'


class ActiveOrders:
    _instance = None
    _lock = Lock()
    _thread = Thread()
    _active_orders = {}
    _api = None

    def __new__(cls, api, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._api = api
        return cls._instance

    def find(self, bot_order_id):
        return self._active_orders.get(bot_order_id, None)

    def add(self, order):
        bot_order_id = order.info['bot_order_id']
        self._active_orders[bot_order_id] = order

    def remove(self, bot_order_id):
        self._active_orders.pop(bot_order_id)

    def all(self):
        return [order.info for order in self._active_orders.values()]

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

