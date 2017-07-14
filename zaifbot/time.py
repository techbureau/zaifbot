# from threading import Lock
# from zaifbot.utils import datetime2timestamp
# from zaifbot.exchange.period import Period
#
#
# class TestingTime:
#     _instance = None
#     _lock = Lock()
#     _from_time = None
#     _to_time = None
#     _size = None
#     _index = None
#     _period = None
#
#     def __new__(cls, **kwargs):
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def __init__(self, from_datetime, to_datetime, period='1m'):
#         self._from_time = datetime2timestamp(from_datetime)
#         self._to_time = datetime2timestamp(to_datetime)
#         self._period = Period(period)
#         self._size = self._period.calc_count(self._from_time, self._to_time)
#         self._index = 0
#
#     def current_time(self):
#         return self._from_time + int(self._period) * self._index
#
#     def update_time(self):
#         self._index += 1
