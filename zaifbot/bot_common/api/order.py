import time
from threading import Thread, Event
from threading import Lock
from datetime import datetime
from abc import ABCMeta, abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.bot_common.errors import ZaifBotError
from zaifbot.bot_common.api.cache import ZaifCurrencyPairs
from zaifbot.bot_common.logger import logger


class AutoCancelClient:
    def __init__(self, trade_api):
        self._auto_cancel_orders = []
        self._trade_api = trade_api

    def cancel_by_time(self, order_id, currency_pair, wait_sec):
        auto_cancel = _AutoCancelByTime(self._trade_api, order_id, currency_pair, wait_sec)
        auto_cancel.start()
        self._auto_cancel_orders.append(auto_cancel)

    def cancel_by_price(self, order_id, currency_pair, target_margin):
        auto_cancel = _AutoCancelByPrice(self._trade_api, order_id, currency_pair, target_margin)
        auto_cancel.start()
        self._auto_cancel_orders.append(auto_cancel)

    def get_active_cancel_orders(self):
        active_cancel_orders = []
        for auto_cancel_order in self._auto_cancel_orders:
            active_cancel_orders.append(auto_cancel_order.get_info())
        return active_cancel_orders

    def stop_cancel(self, order_id, currency_pair):
        cancels = filter(lambda order: order_id == order.order_id and currency_pair == order.currency_pair,
                         self._auto_cancel_orders)
        infos = []
        for cancel in cancels:
            # TODO: これだと、同じ注文に対する複数のキャンセルを区別できない
            cancel.stop()
            cancel.join()
            logger.info('cancel stopped: {{ {} }}'.format(cancel.get_info()))
            infos.append(cancel.get_info())
        return infos


_SLEEP_TIME = 1


class _AutoCancelOrder(Thread, metaclass=ABCMeta):
    def __init__(self, trade_api, order_id, currency_pair):
        super().__init__(daemon=True)
        self.lock = Lock()
        self._private_api = trade_api
        self._order_id = order_id
        self._currency_pair = currency_pair
        self._is_token = self._is_token(currency_pair)
        self._stop_event = Event()
        self._start_time = None
        self._start_price = None

    def run(self):
        self._start_time = time.time()
        self._start_price = get_current_last_price(self._currency_pair)['last_price']
        while self._stop_event.is_set() is False:
            active_orders = self._private_api.active_orders(currency_pair=self._currency_pair)
            if str(self._order_id) not in active_orders:
                self.stop()
                continue
            if self.need_cancel_now():
                self.execute()
            else:
                time.sleep(_SLEEP_TIME)

    @abstractmethod
    def get_info(self):
        raise NotImplementedError

    @abstractmethod
    def need_cancel_now(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
        raise NotImplementedError

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
    def order_id(self):
        return self._order_id

    @property
    def currency_pair(self):
        return self._currency_pair


class _AutoCancelByTime(_AutoCancelOrder):
    def __init__(self, trade_api, order_id, currency_pair, wait_sec):
        super().__init__(trade_api, order_id, currency_pair)
        self._wait_sec = wait_sec
        self._type = 'by_time'

    def execute(self):
        with self.lock:
            self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
            logger.info('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
            self.stop()

    def get_info(self):
        item = {
            'cancel_type': self._type,
            'order_id': self._order_id,
            'currency_pair': self._currency_pair,
            'is_token': self._is_token,
            'current_price': get_current_last_price(self._currency_pair)['last_price'],
            'auto_cancel_started': self._start_time,
            'wait_sec': self._wait_sec,
            'rest_time': self._wait_sec - (time.time() - self._start_time)
        }
        return item

    def need_cancel_now(self):
        if time.time() - self._start_time < self._wait_sec:
            return False
        return True


class _AutoCancelByPrice(_AutoCancelOrder):
    def __init__(self, trade_api, order_id, currency_pair, target_margin):
        super().__init__(trade_api, order_id, currency_pair)
        self._target_margin = target_margin
        self._currency_pair = currency_pair
        self._type = 'by_price'

    def get_info(self):
        last_price = get_current_last_price(self._currency_pair)['last_price']
        item = {
            'cancel_type': self._type,
            'order_id': self._order_id,
            'currency_pair': self._currency_pair,
            'is_token': self._is_token,
            'current_price': last_price,
            'auto_cancel_started': self._start_time,
            'start_price': self._start_price,
            'target_margin': self._target_margin,
            'current_margin': abs(last_price - self._start_price),
        }
        return item

    def execute(self):
        with self.lock:
            self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
            logger.info('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
            self.stop()

    def need_cancel_now(self):
        last_price = get_current_last_price(self._currency_pair)['last_price']
        if abs(self._start_price - last_price) < self._target_margin:
            return False
        return True
