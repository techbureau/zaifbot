from abc import ABCMeta, abstractmethod
from zaifapi.impl import ZaifPrivateApi
import time
from zaifbot.bot_common.utils import get_current_last_price


class CancelOrder(metaclass=ABCMeta):
    def __init__(self, key, secret, order_id):
        self._private_api = ZaifPrivateApi(key, secret)
        self._order_id = order_id

    @abstractmethod
    def execute(self):
        raise NotImplementedError


class CancelByTime(CancelOrder):
    def __init__(self, key, secret, order_id, time_limit):
        super().__init__(key, secret, order_id)
        self._time_limit = time_limit

    def execute(self):
        start = time.time()
        while True:
            if time.time() - start >= self._time_limit:
                self._private_api.cancel_order(order_id=self._order_id)
            else:
                time.sleep(1)


class CancelByPrice(CancelOrder):
    def __init__(self, key, secret, order_id, pricediff):
        super().__init__(key, secret, order_id)
        self._pricediff = pricediff
        self._type = self._private_api.active_orders()['return']['active_orders'][self._order_id]['action']
        self._currency_pair = self._private_api.active_orders()['return']['active_orders'][self._order_id]['currency_pair']
        self._price =  self._private_api.active_orders()['return']['active_orders'][self._order_id]['price']

    def execute(self):
        if self._type == 'bid':
            while True:
                last_price = get_current_last_price(self._currency_pair)
                if last_price - self._price >= self._pricediff:
                    self._private_api.cancel_order(order_id=self._order_id)
                else:
                    time.sleep(1)
        else:
            while True:
                last_price = get_current_last_price(self._currency_pair)
                if self._price - last_price >= self._pricediff:
                    self._private_api.cancel_order(order_id=self._order_id)
                else:
                    time.sleep(1)


if __name__ == "__main__":
    time = CancelByTime('a', 'c', 'id', 'time')
    print(time.execute())