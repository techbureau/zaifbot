import time
from threading import Event
from zaifbot.api.orders.common import AutoCancelOrder


class TimeLimitCancel(AutoCancelOrder):
    def __init__(self, api, target_order_id, currency_pair, wait_sec, comment=''):
        super().__init__(api, currency_pair, comment)
        self._target_order_id = target_order_id
        self._wait_sec = wait_sec
        self._start_time = None
        self._stop_event = Event()

    @property
    def type(self):
        return 'TimeLimitCancel'

    def info(self):
        info = super().info
        info['wait_sec'] = self._wait_sec
        info['rest_time'] = self._wait_sec - (time.time() - self._start_time)
        return info

    def make_order(self, *args, **kwargs):
        self._started_time = int(time.time())
        self.start()

    def _can_execute(self):
        if time.time() - self._start_time < self._wait_sec:
            return False
        return True
