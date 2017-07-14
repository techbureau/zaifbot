from threading import Thread, Event, Lock

from zaifapi.impl import ZaifPublicStreamApi

from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.logger import bot_logger


class BotStreamApi:
    _lock = Lock()
    _sockets = {}
    _stop_events = {}
    _error_events = {}
    _instance = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def execute(self, currency_pair):
        if isinstance(currency_pair, CurrencyPair):
            if currency_pair.is_token:
                raise ValueError('token is not supported by stream api')

        currency_pair = str(currency_pair)
        if self._sockets.get(currency_pair, None):
            return self._sockets[currency_pair].execute(currency_pair)
        self._run_new_socket(currency_pair)

        return self._sockets[currency_pair].last_receive

    def stop(self, currency_pair):
        if self._stop_events.get(currency_pair, None):
            self._sockets[currency_pair].stop()
        else:
            pass

    def _run_new_socket(self, currency_pair):
        if self._sockets.get(currency_pair, None):
            return
        stop_event = Event()
        error_event = Event()
        new_socket = _StreamThread(currency_pair, stop_event, error_event)
        new_socket.start()
        self._sockets[currency_pair] = new_socket
        self._stop_events[currency_pair] = stop_event
        self._error_events[currency_pair] = error_event


class _StreamThread(Thread):
    def __init__(self, currency_pair, stop_event, error_event):
        self._currency_pair = str(currency_pair)
        self._stop_event = stop_event
        self._error_event = error_event
        self._last_receive = None
        self._socket = ZaifPublicStreamApi()

        super().__init__(name='{}_wss_stream'.format(currency_pair), daemon=True)
        self._activate_socket()

    def run(self):
        try:
            for receive in self._socket.execute(self._currency_pair):
                self._last_receive = receive
                if self._stop_event.is_set():
                    self._socket.stop()
        except Exception as e:
            bot_logger.exception(e)
            self._error_event.set()

    def _activate_socket(self):
        self._last_receive = next(self._socket.execute(self._currency_pair))

    @property
    def last_receive(self):
        return self._last_receive
