import time
from threading import Event
from zaifbot.order.orders.common import AutoCancelOrder, log_after_trade


class TimeLimitCancel(AutoCancelOrder):
    def __init__(self, api, target_bot_order_id, currency_pair, wait_sec, comment=''):
        super().__init__(api, target_bot_order_id, currency_pair, comment)
        self._wait_sec = wait_sec
        self._start_time = int(time.time())
        self._stop_event = Event()

    @property
    def type(self):
        return 'TimeLimitCancel'

    @property
    def info(self):
        info = super().info
        info['wait_sec'] = self._wait_sec
        info['rest_time'] = self._wait_sec - (int(time.time()) - self._start_time)
        return info

    @log_after_trade('order made')
    def make_order(self, *args, **kwargs):
        self._started_time = int(time.time())
        self.start()
        return self

    def _can_execute(self):
        if time.time() - self._start_time < self._wait_sec:
            return False
        return True
