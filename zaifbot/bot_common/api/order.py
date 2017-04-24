from abc import ABCMeta, abstractmethod
from zaifapi.impl import ZaifPrivateApi
import time
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.bot_common.utils import logger


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
                try:
                    self._private_api.cancel_order(order_id=self._order_id)
                    break
                except Exception as e:
                    logger.error(e)
            else:
                time.sleep(1)


class CancelByPrice(CancelOrder):
    def __init__(self, key, secret, order_id, price_diff):
        super().__init__(key, secret, order_id)
        self._price_diff = price_diff

        self._type = self._private_api.active_orders()['return']['active_orders'][self._order_id]['action']
        self._currency_pair = self._private_api.active_orders()['return']['active_orders'][self._order_id]['currency_pair']
        self._price = self._private_api.active_orders()['return']['active_orders'][self._order_id]['price']

    def execute(self):
        try:
            order = self._private_api.active_orders()['return']['active_orders'][self._order_id]
        except Exception as e:
            logger.error(e)

        while True:
            last_price = get_current_last_price(order['currency_pair'])
            if order['action'] == 'bid':
                if last_price - order['price'] >= self._price_diff:
                    try:
                        self._private_api.cancel_order(order_id=self._order_id)
                        break
                    except Exception as e:
                        logger.error(e)
                else:
                    time.sleep(1)
            else:
                if order['price'] - last_price >= self._price_diff:
                    try:
                        self._private_api.cancel_order(order_id=self._order_id)
                        break
                    except Exception as e:
                        logger.error(e)
                else:
                    time.sleep(1)