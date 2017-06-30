from threading import Event
from zaifbot.api.orders.common import AutoCancelOrder


class PriceBoundaryCancel(AutoCancelOrder):
    def __init__(self, trade_api, target_bot_order_id, currency_pair, target_margin, comment=''):
        super().__init__(trade_api, target_bot_order_id, currency_pair, comment)
        self._target_margin = target_margin
        self._start_price = None
        self._stop_event = Event()

    @property
    def type(self):
        return 'PriceBoundaryCancel'

    @property
    def info(self):
        info = super().info
        info['start_price'] = self._start_price
        info['target_margin'] = self._target_margin
        info['current_margin'] = abs(self._currency_pair.last_price()['last_price'] - self._start_price)
        return info

    def make_order(self, *args, **kwargs):
        self._start_price = self._currency_pair.last_price()['last_price']
        self.start()
        return self

    def _can_execute(self):
        last_price = self._currency_pair.last_price()['last_price']
        if abs(self._start_price - last_price) < self._target_margin:
            return False
        return True
