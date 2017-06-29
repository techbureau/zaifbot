# import time
# from abc import ABCMeta, abstractmethod
# from threading import Thread, Event
# from zaifbot.currency_pairs import CurrencyPair
# from zaifbot.api.orders.common import ActiveOrders, BotOrderID
#
#
# class AutoCancel:
#     def __init__(self, trade_api):
#         self._trade_api = trade_api
#         self._active_orders = ActiveOrders(self._trade_api)
#
#     def time_limit_cancel(self, bot_order_id, currency_pair, wait_sec):
#         auto_cancel = _AutoCancelByTime(self._trade_api, bot_order_id, currency_pair, wait_sec)
#         self._active_orders.add(auto_cancel)
#         auto_cancel.start()
#         return auto_cancel.info
#
#     def price_range_cancel(self, bot_order_id, currency_pair, target_margin):
#         auto_cancel = _AutoCancelByPrice(self._trade_api, bot_order_id, currency_pair, target_margin)
#         self._active_orders.add(auto_cancel)
#         auto_cancel.start()
#         return auto_cancel.info
#
# _SLEEP_TIME = 1
#
#
# class _AutoCancelOrder(Thread, metaclass=ABCMeta):
#     def __init__(self, trade_api, target_bot_order_id, currency_pair):
#         super().__init__(daemon=True)
#         self._api = trade_api
#         self._active_orders = ActiveOrders(self._api)
#         self._bot_order_id = str(BotOrderID())
#         self._target_bot_order_id = target_bot_order_id
#         self._currency_pair = CurrencyPair(currency_pair)
#         self._is_token = self._is_token(currency_pair)
#         self._stop_event = Event()
#         self._start_time = None
#
#     def run(self):
#         self._start_time = int(time.time())
#         while self._stop_event.is_set() is False:
#             active_orders = self._active_orders.all()
#             print(active_orders)
#             print('d')
#             if self._target_bot_order_id not in active_orders:
#                 self.stop()
#                 continue
#             if self._can_execute():
#                 print('test')
#                 self._execute()
#             else:
#                 time.sleep(_SLEEP_TIME)
#
#     @property
#     def info(self):
#         info = {
#             'bot_order_id': self._bot_order_id,
#             'name': self.name,
#             'target_bot_order_id': self._target_bot_order_id,
#             'currency_pair': str(self._currency_pair),
#             'is_token': self._is_token,
#             'started': self._start_time,
#         }
#         return info
#
#     def _execute(self):
#         self._api.cancel_order(order_id=self._target_bot_order_id, is_token=self._is_token)
#         self.stop()
#
#     def stop(self):
#         self._stop_event.set()
#
#     @property
#     @abstractmethod
#     def name(self):
#         raise NotImplementedError
#
#     @abstractmethod
#     def _can_execute(self):
#         raise NotImplementedError
#
#
# class _AutoCancelByTime(_AutoCancelOrder):
#     def __init__(self, trade_api, order_id, currency_pair, wait_sec):
#         super().__init__(trade_api, order_id, currency_pair)
#         self._wait_sec = wait_sec
#
#     @property
#     def info(self):
#         info = super().info
#         info['wait_sec'] = self._wait_sec
#         info['rest_time'] = self._wait_sec - (time.time() - self._start_time)
#         return info
#
#     def _can_execute(self):
#         if time.time() - self._start_time < self._wait_sec:
#             return False
#         return True
#
#     @property
#     def name(self):
#         return 'TimeLimitCancel'
#
#
# class _AutoCancelByPrice(_AutoCancelOrder):
#     def __init__(self, trade_api, order_id, currency_pair, target_margin):
#         super().__init__(trade_api, order_id, currency_pair)
#         self._target_margin = target_margin
#         self._currency_pair = CurrencyPair(currency_pair)
#         self._start_price = None
#
#     @property
#     def info(self):
#         info = super().info
#         info['start_price'] = self._start_price
#         info['target_margin'] = self._target_margin
#         info['current_margin'] = abs(info['current_price'] - self._start_price)
#         return info
#
#     def run(self):
#         self._start_price = self._currency_pair.last_price()['last_price']
#         super().run()
#
#     def _can_execute(self):
#         last_price = self._currency_pair.last_price()['last_price']
#         if abs(self._start_price - last_price) < self._target_margin:
#             return False
#         return True
#
#     @property
#     def name(self):
#         return 'PriceRangeCancel'
