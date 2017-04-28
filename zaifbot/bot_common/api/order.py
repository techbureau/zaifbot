import time
import traceback
from datetime import datetime
from abc import ABCMeta, abstractmethod
from zaifbot.bot_common.api.wrapper import BotTradeApi
from zaifbot.bot_common.utils import get_current_last_price, logger
from zaifbot.bot_common.errors import ZaifBotError
from .cache import ZaifCurrencyPairs


class CancelOrder(metaclass=ABCMeta):
    def __init__(self, key, secret, order_id, currency_pair):
        self._private_api = BotTradeApi(key, secret)
        self._order_id = order_id
        self._is_token = self._is_token(currency_pair)

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @staticmethod
    def _is_token(currency_pair):
        currency_pairs = ZaifCurrencyPairs()
        record = currency_pairs[currency_pair]
        if record:
            return record['is_token']
        raise ZaifBotError('illegal currency_pair:{}'.format(currency_pair))


class CancelByTime(CancelOrder):
    def __init__(self, key, secret, order_id, currency_pair, time_limit_sec):
        super().__init__(key, secret, order_id, currency_pair)
        self._time_limit_sec = time_limit_sec

    def execute(self):
        start = time.time()
        while True:
            if time.time() - start >= self._time_limit_sec:
                try:
                    self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
                    print('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error(traceback.format_exc())
            else:
                time.sleep(1)


class CancelByPrice(CancelOrder):
    def __init__(self, key, secret, order_id, currency_pair, price_diff):
        super().__init__(key, secret, order_id, currency_pair)
        self._price_diff = price_diff
        self._currency_pair = currency_pair

    def execute(self):
        while True:
            try:
                active_orders = self._private_api.active_orders(currency_pair=self._currency_pair)
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                return
            if str(self._order_id) not in active_orders:
                return
            order_price = active_orders[str(self._order_id)]['price']
            last_price = get_current_last_price(self._currency_pair)
            if abs(order_price - last_price) < self._price_diff:
                time.sleep(1)
                continue
            try:
                self._private_api.cancel_order(order_id=self._order_id, is_token=self._is_token)
                print('order canceled \n {{order_id: {0}, timestamp: {1}}}'.format(self._order_id, datetime.now()))
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                return
