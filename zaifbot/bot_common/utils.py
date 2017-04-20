import json
import threading
from threading import Thread, Event
from websocket import create_connection
from zaifapi.impl import ZaifPublicApi, ZaifPrivateApi, ZaifPublicStreamApi
from zaifbot.bot_common.config import load_config
from zaifbot.bot_common.save_trade_log import save_trade_log
from zaifbot.bot_common.logger import logger
from time import time


class _ZaifWebSocket:
    _instance = None
    _lock = threading.Lock()
    _threads = {}
    _stop_events = {}
    _last_prices = {}

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def last_price(self, currency_pair):
        if currency_pair not in self._threads:
            self._create_stream_thread(currency_pair)
        target_thread = self._threads[currency_pair]
        if target_thread.is_error_happened:
            self._create_stream_thread(currency_pair)
        if target_thread.is_alive() is False:
            raise Exception('だめだめでした')
        return target_thread.last_price

    def _create_stream_thread(self, currency_pair):
        stop_event = Event()
        error_event = Event()
        thread_obj = _StreamThread(currency_pair, stop_event, error_event)
        thread_obj.start()
        self._threads[currency_pair] = thread_obj
        self._stop_events[currency_pair] = stop_event

    def close_all_socket(self):
        [event.set() for event in self._stop_events.values()]
        [thread.join() for thread in self._threads.values()]


class _StreamThread(Thread):

    def __init__(self, currency_pair, stop_event, error_event):
        super(_StreamThread, self).__init__(name='{}_wss_stream'.format(currency_pair), daemon=True)
        self._currency_pair = currency_pair
        self._stop_event = stop_event
        self._last_price = None
        self._stream_api = ZaifPublicStreamApi()
        self._set_first_last_price()
        self._error_event = error_event

    def run(self):
        try:
            for receive in self._stream_api.execute(self._currency_pair):
                self._set_last_price(receive)
                if self._stop_event.is_set():
                    self._stream_api.stop()
        except:
            self._error_event.set()

    def _set_first_last_price(self):
        receive = self._stream_api.execute(self._currency_pair).next()
        self._set_last_price(receive)

    def _set_last_price(self, receive):
        self._last_price = {'timestamp': receive['timestamp'], 'last_price': receive['last_price']}

    @property
    def is_error_happened(self):
        return self._error_event.is_set()

    @property
    def last_price(self):
        return self._last_price


def get_current_last_price(currency_pair):
    api = _ZaifWebSocket()
    return api.last_price(currency_pair)


class ZaifOrder:
    def __init__(self):
        self._config = load_config()
        self._private_api = ZaifPrivateApi(self._config.api_keys.key, self._config.api_keys.secret)

    def get_active_orders(self):
        try:
            return self._private_api.active_orders(currency_pair=self._config.system.currency_pair,
                                                   is_token_both=True)
        except Exception:
            return {}

    def trade(self, action, price, amount, limit=None):
        try:
            if limit:
                self._private_api.trade(currency_pair=self._config.system.currency_pair,
                                        action=action,
                                        price=price,
                                        amount=amount,
                                        limit=limit)
                trade_log = {
                    'time': time(),
                    'action': action,
                    'currency_pair': self._config.system.currency_pair,
                    'price': price,
                    'amount': amount,
                    'limit': limit
                    }
            else:
                self._private_api.trade(currency_pair=self._config.system.currency_pair,
                                        action=action,
                                        price=price,
                                        amount=amount)
                trade_log = {
                    'time': time(),
                    'action': action,
                    'currency_pair': self._config.system.currency_pair,
                    'price': price,
                    'amount': amount
                    }
            save_trade_log(trade_log)
        except Exception as e:
            logger.error(e)

    def cancel_order(self, order_id):
        try:
            self._private_api.cancel_order(order_id=order_id)
        except Exception:
            False

    def get_last_trade_history(self):
        try:
            return self._private_api.trade_history(currency_pair=self._config.system.currency_pair,
                                                   order='DESC',
                                                   count=1)
        except Exception as e:
            return e


if __name__ == '__main__':
    print(get_current_last_price('btc_jpy'))
