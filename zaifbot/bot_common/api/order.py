import time
import traceback
from threading import Thread, Event
from datetime import datetime
from abc import ABCMeta, abstractmethod
from zaifbot.bot_common.api.wrapper import BotTradeApi
from zaifbot.bot_common.utils import get_current_last_price, logger
from zaifbot.bot_common.errors import ZaifBotError
from zaifbot.bot_common.api.cache import ZaifCurrencyPairs


class AutoCancelClient:
    def __init__(self, key, secret):
        self._cancel_requests = []
        self._key = key
        self._secret = secret

    def cancel_by_time(self, order_id, currency_pair, wait_sec):
        request = CancelByTime(self._key, self._secret, order_id, currency_pair, wait_sec)
        request.run()
        self._cancel_requests.append(request)

    def cancel_by_price(self, order_id, currency_pair, target_price_gap):
        request = CancelByPrice(self._key, self._secret, order_id, currency_pair, target_price_gap)
        request.run()
        self._cancel_requests.append(request)

    def get_active_order(self):
        active_orders = []
        for request in self._cancel_requests:
            active_orders.append(request.get_info())
        return active_orders

    @staticmethod
    def take_back_cancel(order):
        order.stop()


class CancelOrder(Thread, metaclass=ABCMeta):
    def __init__(self, key, secret, order_id, currency_pair):
        super().__init__(daemon=True)
        self._private_api = BotTradeApi(key, secret)
        self._order_id = order_id
        self._currency_pair = currency_pair
        self._is_token = self._is_token(currency_pair)
        self._stop_event = Event()
        self._type = None

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @abstractmethod
    def get_info(self):
        raise NotImplementedError

    def stop(self):
        self._stop_event = True

    @staticmethod
    def _is_token(currency_pair):
        currency_pairs = ZaifCurrencyPairs()
        record = currency_pairs[currency_pair]
        if record:
            return record['is_token']
        raise ZaifBotError('illegal currency_pair:{}'.format(currency_pair))


class CancelByTime(CancelOrder):
    def __init__(self, key, secret, order_id, currency_pair, wait_sec):
        super().__init__(key, secret, order_id, currency_pair)
        self._wait_sec = wait_sec
        self._type = 'by_time'
        self._start = None

    def run(self):
        self._start = time.time()
        while self._stop_event.is_set() is False:
            if time.time() - self._start >= self._wait_sec:
                try:
                    self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
                    print('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error(traceback.format_exc())
            else:
                time.sleep(1)

    def get_info(self):
        item = {
            'cancel_type': self._type,
            'id': self._order_id,
            'currency_pair': self._currency_pair,
            'last_price': get_current_last_price(self._currency_pair),
            'start_time': self._start,
            'wait_sec': self._wait_sec,
            'rest_time': self._wait_sec - (time.time() - self._start)
        }
        return item


class CancelByPrice(CancelOrder):
    def __init__(self, key, secret, order_id, currency_pair, target_price_gap):
        super().__init__(key, secret, order_id, currency_pair)
        self._target_price_gap = target_price_gap
        self._currency_pair = currency_pair
        self._type = 'by_price'
        self._start_price = None
        self._start = None

    def get_info(self):
        last_price = get_current_last_price(self._currency_pair)
        item = {
            'cancel_type': self._type,
            'id': self._order_id,
            'currency_pair': self._currency_pair,
            'last_price': last_price,
            'start_time': self._start,
            'start_price': self._start_price,
            'target_price_gap': self._target_price_gap,
            'current_gap': abs(last_price - self._start_price),
        }
        return item

    def run(self):
        self._start = time.time()
        while self._stop_event.is_set() is False:
            try:
                active_orders = self._private_api.active_orders(currency_pair=self._currency_pair)
                self._start_price = active_orders[str(self._order_id)]['price']
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                return
            if str(self._order_id) not in active_orders:
                return
            order_price = active_orders[str(self._order_id)]['price']
            last_price = get_current_last_price(self._currency_pair)
            if abs(order_price - last_price) < self._target_price_gap:
                time.sleep(1)
                continue
            try:
                self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
                print('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                return
