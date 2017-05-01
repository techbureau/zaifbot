import time
from threading import Thread, Event
from datetime import datetime
from zaifbot.bot_common.logger import logger
from abc import ABCMeta, abstractmethod
from zaifbot.bot_common.api.wrapper import BotTradeApi
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.bot_common.errors import ZaifBotError
from zaifbot.bot_common.api.cache import ZaifCurrencyPairs


class AutoCancelClient:
    def __init__(self, key, secret):
        self._auto_cancels_orders = []
        self._key = key
        self._secret = secret

    def cancel_by_time(self, order_id, currency_pair, wait_sec):
        auto_cancel = _AutoCancelByTime(self._key, self._secret, order_id, currency_pair, wait_sec)
        auto_cancel.start()
        self._auto_cancels_orders.append(auto_cancel)

    def cancel_by_price(self, order_id, currency_pair, target_margin):
        auto_cancel = _AutoCancelByPrice(self._key, self._secret, order_id, currency_pair, target_margin)
        auto_cancel.start()
        self._auto_cancels_orders.append(auto_cancel)

    def get_active_cancel_orders(self):
        active_cancel_orders = []
        for auto_cancel_order in self._auto_cancels_orders:
            active_cancel_orders.append(auto_cancel_order.get_info())
        return active_cancel_orders

    def take_back_cancel(self, cancel_id):
        for cancel_order in self._auto_cancels_orders:
            if cancel_id == id(cancel_order):
                cancel_order._stop_event = True
                return
            

class _AutoCancelOrder(Thread, metaclass=ABCMeta):
    def __init__(self, key, secret, order_id, currency_pair):
        super().__init__()
        self._private_api = BotTradeApi(key, secret)
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
            #active_orders = self._private_api.active_orders(currency_pair=self._currency_pair)
            #self._start_price = active_orders[str(self._order_id)]['price']
            if self.is_able_to_cancel():
                self.try_cancel()
            else:
                time.sleep(1)

    @abstractmethod
    def get_info(self):
        raise NotImplementedError

    @abstractmethod
    def is_able_to_cancel(self):
        raise NotImplementedError

    @abstractmethod
    def try_cancel(self):
        raise NotImplementedError

    @staticmethod
    def _is_token(currency_pair):
        currency_pairs = ZaifCurrencyPairs()
        record = currency_pairs[currency_pair]
        if record:
            return record['is_token']
        raise ZaifBotError('illegal currency_pair:{}'.format(currency_pair))

    def _stop(self):
        self._stop_event.set()


class _AutoCancelByTime(_AutoCancelOrder):
    def __init__(self, key, secret, order_id, currency_pair, wait_sec):
        super().__init__(key, secret, order_id, currency_pair)
        self._wait_sec = wait_sec
        self._type = 'by_time'

    def try_cancel(self):
        self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
        print('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
        self._stop()

    def get_info(self):
        item = {
            'id': id(self),
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

    def is_able_to_cancel(self):
        active_orders = self._private_api.active_orders(currency_pair=self._currency_pair)
        if str(self._order_id) not in active_orders:
            return False
        return True if time.time() - self._start_time >= self._wait_sec else False


class _AutoCancelByPrice(_AutoCancelOrder):
    def __init__(self, key, secret, order_id, currency_pair, target_margin):
        super().__init__(key, secret, order_id, currency_pair)
        self._target_margin = target_margin
        self._currency_pair = currency_pair
        self._type = 'by_price'

    def get_info(self):
        last_price = get_current_last_price(self._currency_pair)['last_price']
        item = {
            'id': id(self),
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

    def try_cancel(self):
        self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
        print('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
        self._stop()

    def is_able_to_cancel(self):
        active_orders = self._private_api.active_orders(currency_pair=self._currency_pair)
        #self._start_price = active_orders[str(self._order_id)]['price']
        if str(self._order_id) not in active_orders:
            return False
        last_price = get_current_last_price(self._currency_pair)['last_price']
        logger.error(last_price)
        logger.error(self._start_price)
        if abs(self._start_price - last_price) > self._target_margin:
            return True
        else:
            return False
