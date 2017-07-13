from threading import Thread, Event, Lock
from zaifapi.impl import ZaifPublicStreamApi
from zaifbot.api_manage import APIRepository
from zaifbot.common.errors import ZaifBotError
from zaifbot.common.logger import bot_logger
from zaifbot.exchange.currency_pairs import CurrencyPair


class BotStreamApi:
    _lock = Lock()
    _threads = {}
    _stop_events = {}
    _error_events = {}

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def latest_price(self, currency_pair):
        if isinstance(currency_pair, CurrencyPair):
            currency_pair = str(currency_pair)
        if self._threads.get(currency_pair, None):
            return self._threads[currency_pair].execute(currency_pair)
        self._run_new_socket(currency_pair)

    def _run_new_socket(self, currency_pair):
        if self._threads.get(currency_pair, None):
            return
        stop_event = Event()
        error_event = Event()
        new_thread = _StreamThread(currency_pair, stop_event, error_event)
        new_thread.start()
        self._threads[currency_pair] = new_thread
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


#############

# def latest_closing_price(currency_pair):
#     closing_price = _ClosingPrice()
#     return closing_price.latest_price(currency_pair)


# class _ClosingPrice:
#     _instance = None
#     _lock = Lock()
#     _threads = {}
#     _stop_events = {}
#
#     def __new__(cls):
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def latest_price(self, currency_pair):
#         currency_pair = CurrencyPair(currency_pair)
#         if currency_pair.is_token:
#             api = APIRepository().public_api
#             return api.last_price(currency_pair)['last_price']
#
#         receive = self._get_target_thread(currency_pair).last_receive
#         return receive['last_price']['price']
#
#     def close_all_socket(self):
#         [event.set() for event in self._stop_events.values()]
#         [thread.join() for thread in self._threads.values()]
#
#     def _get_target_thread(self, currency_pair):
#         def create_stream_thread():
#             stop_event = Event()
#             error_event = Event()
#             thread_obj = _StreamThread(currency_pair, stop_event, error_event)
#             thread_obj.start()
#             self._threads[currency_pair] = thread_obj
#             self._stop_events[currency_pair] = stop_event
#
#         if currency_pair not in self._threads:
#             create_stream_thread()
#         if self._threads[currency_pair].is_error_happened:
#             create_stream_thread()
#         if self._threads[currency_pair].is_alive() is False:
#             raise ZaifBotError('thread is dead')
#         return self._threads[currency_pair]
#
#
