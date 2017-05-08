import time
from threading import Thread, Event
from datetime import datetime
from uuid import uuid4
from abc import ABCMeta, abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.bot_common.errors import ZaifBotError
from zaifbot.bot_common.api.cache import ZaifCurrencyPairs
from zaifbot.bot_common.logger import logger


class AutoCancelClient:
    def __init__(self, trade_api):
        self._auto_cancel_orders = {}
        self._trade_api = trade_api

    def cancel_by_time(self, order_id, currency_pair, wait_sec):
        auto_cancel = _AutoCancelByTime(self._trade_api, order_id, currency_pair, wait_sec)
        auto_cancel.start()
        self._auto_cancel_orders[auto_cancel.id] = auto_cancel
        return auto_cancel.get_info()

    def cancel_by_price(self, order_id, currency_pair, target_margin):
        auto_cancel = _AutoCancelByPrice(self._trade_api, order_id, currency_pair, target_margin)
        auto_cancel.start()
        self._auto_cancel_orders[auto_cancel.id] = auto_cancel
        return auto_cancel.get_info()

    def get_active_cancel_orders(self):
        self._remove_dead_threads()
        active_cancel_orders = []
        for auto_cancel_order in self._auto_cancel_orders.values():
            active_cancel_orders.append(auto_cancel_order.get_info())
        return active_cancel_orders

    def stop_cancel(self, cancel_id):
        self._remove_dead_threads()
        cancel_order = self._auto_cancel_orders.get(cancel_id, None)
        if cancel_order is None:
            logger.warn('couldn\'t find cancel_id you gave : {}'.format(cancel_id))
            return
        cancel_order.stop()
        cancel_order.join()
        logger.info('cancel stopped: {{ {} }}'.format(cancel_order.get_info()))
        self._remove_dead_threads()
        return cancel_order.get_info()

    def _remove_dead_threads(self):
        delete_cancel_ids = []
        for cancel_id, cancel_thread in self._auto_cancel_orders.items():
            if cancel_thread.is_alive() is False:
                delete_cancel_ids.append(cancel_id)
        for cancel_id in delete_cancel_ids:
            del self._auto_cancel_orders[cancel_id]


_SLEEP_TIME = 1


class _AutoCancelOrder(Thread, metaclass=ABCMeta):
    def __init__(self, trade_api, order_id, currency_pair):
        super().__init__(daemon=True)
        self._private_api = trade_api
        self._id = str(uuid4())
        self._order_id = order_id
        self._currency_pair = currency_pair
        self._is_token = self._is_token(currency_pair)
        self._stop_event = Event()
        self._start_time = None

    def run(self):
        self._start_time = time.time()
        while self._stop_event.is_set() is False:
            active_orders = self._private_api.active_orders(currency_pair=self._currency_pair)
            if str(self._order_id) not in active_orders:
                self.stop()
                continue
            if self._need_cancel_now():
                self._execute()
            else:
                time.sleep(_SLEEP_TIME)

    def get_info(self):
        info = {
            'id': self.id,
            'cancel_type': self.get_type(),
            'order_id': self._order_id,
            'currency_pair': self._currency_pair,
            'is_token': self._is_token,
            'current_price': get_current_last_price(self._currency_pair)['last_price'],
            'auto_cancel_started': self._start_time,
        }
        return info

    def _execute(self):
        self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
        logger.info('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
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
    def id(self):
        return self._id

    @abstractmethod
    def get_type(self):
        raise NotImplementedError

    @abstractmethod
    def _need_cancel_now(self):
        raise NotImplementedError


class _AutoCancelByTime(_AutoCancelOrder):
    def __init__(self, trade_api, order_id, currency_pair, wait_sec):
        super().__init__(trade_api, order_id, currency_pair)
        self._wait_sec = wait_sec

    def get_info(self):
        info = super().get_info()
        info['wait_sec'] = self._wait_sec
        info['rest_time'] = self._wait_sec - (time.time() - self._start_time)
        return info

    def _need_cancel_now(self):
        if time.time() - self._start_time < self._wait_sec:
            return False
        return True

    def get_type(self):
        return 'by_time'


class _AutoCancelByPrice(_AutoCancelOrder):
    def __init__(self, trade_api, order_id, currency_pair, target_margin):
        super().__init__(trade_api, order_id, currency_pair)
        self._target_margin = target_margin
        self._currency_pair = currency_pair
        self._start_price = None

    def get_info(self):
        info = super().get_info()
        info['start_price'] = self._start_price
        info['target_margin'] = self._target_margin
        info['current_margin'] = abs(info['current_price'] - self._start_price)
        return info

    def run(self):
        self._start_price = get_current_last_price(self._currency_pair)['last_price']
        super().run()

    def _need_cancel_now(self):
        last_price = get_current_last_price(self._currency_pair)['last_price']
        if abs(self._start_price - last_price) < self._target_margin:
            return False
        return True

    def get_type(self):
        return 'by_price'
