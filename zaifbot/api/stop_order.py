from zaifbot.price.utils import get_current_last_price, get_buyable_amount
from time import sleep, time
from zaifbot.bot_common.bot_const import BUY, SELL, CANCEL, TRADE_ACTION
from threading import Thread
from abc import ABCMeta, abstractmethod
from uuid import uuid4
from zaifbot.bot_common.logger import logger
from datetime import datetime


class StopOrderClient:
    def __init__(self, trade_api):
        self._stop_orders = {}
        self._trade_api = trade_api

    def stop_order_buy(self, stop_order_id, trade_params):
        stop_order = _StopOrderBuy(self._trade_api, stop_order_id, trade_params)
        stop_order.start()
        self._stop_orders[stop_order.id] = stop_order
        return stop_order.get_info()

    def stop_order_sell(self, stop_order_id, trade_params):
        stop_order = _StopOrderSell(self._trade_api, stop_order_id, trade_params)
        stop_order.start()
        self._stop_orders[stop_order.id] = stop_order
        return stop_order.get_info()

    def get_active_stop_orders(self):
        self._remove_dead_threads()
        active_stop_orders = []
        for stop_order in self._stop_orders.values():
            active_stop_orders.append(stop_order.get_info())
        return active_stop_orders

    def cancel_stop_order(self, stop_order_id):
        self._remove_dead_threads()
        cancel_stop_order = self._stop_orders.get(stop_order_id, None)
        if cancel_stop_order is None:
            logger.warn('couldn\'t find stop_order_id you gave : {}'.format(stop_order_id))
            return
        cancel_stop_order._cancel = True
        logger.info('stop order is cancelled: {{ {} }}'.format(cancel_stop_order.get_info()))
        self._remove_dead_threads()
        return cancel_stop_order.get_info()

    def _remove_dead_threads(self):
        delete_cancel_ids = []
        delete_stop_order_ids = []
        for stop_order_id, stop_order_thread in self._stop_orders.items():
            if stop_order_thread.is_alive() is False:
                delete_stop_order_ids.append(stop_order_id)
        for stop_order_id in delete_stop_order_ids:
            del self._stop_orders[stop_order_id]


class _StopOrder(Thread, metaclass=ABCMeta):
    def __init__(self, trade_api, stop_order_id, trade_params):
        super().__init__(daemon=True)
        self._trade_api = trade_api
        self._stop_order_id = stop_order_id
        self._sleep_time = trade_params['sleep_time']
        self._target_price = trade_params['target_price']
        self._trade_price_margin = trade_params['trade_price_margin']
        self._currency_pair = trade_params['currency_pair']
        self._amount = trade_params['amount']
        self._cancel = False
        self._id = str(uuid4())

    def run(self):
        self._start_time = time()
        while self._cancel is False:
            sleep(self._sleep_time)
            if self._is_started() is False:
                continue
            self._execute()
            break

    def _is_started(self):
        current_last_price = get_current_last_price(self._currency_pair)
        if current_last_price is None:
            return False
        self._last_price = int(current_last_price['last_price'])
        return self._check_stop_order()

    def _execute(self):
        if self._cancel:
            return True
        order = self._order()
        if order['order_id'] is None:
            logger.warn('failed to order : {}'.format(stop_order_id))
        logger.info('stop order \n {{stop_order_id: {0}, timestamp: {1}}}'
                    .format(self._stop_order_id, datetime.now()))

    @abstractmethod
    def _check_stop_order(self):
        raise NotImplementedError

    @abstractmethod
    def get_type(self):
        raise NotImplementedError

    @property
    def id(self):
        return self._id

    def get_info(self):
        info = {
            'id': self.id,
            'stop_order_type': self.get_type(),
            'order_id': self._stop_order_id,
            'currency_pair': self._currency_pair,
            'current_price': get_current_last_price(self._currency_pair)['last_price'],
            'amount': self._amount,
            'target_price': self._target_price,
            'trade_price_margin': self._trade_price_margin,
            'stop_order_started': self._start_time,
        }
        return info


class _StopOrderBuy(_StopOrder):
    def __init__(self, trade_api, stop_order_id, trade_params):
        super().__init__(trade_api, stop_order_id, trade_params)

    def _check_stop_order(self):
        if self._last_price >= self._target_price:
            if self._last_price >= (self._target_price + self._trade_price_margin):
                self._cancel = True
            return True
        return False

    def _order(self):
        amount = get_buyable_amount(self._currency_pair, self._amount, self._last_price)
        return self._trade_api.trade(currency_pair=self._currency_pair,
                               action='bid', price=self._last_price, amount=amount)

    def get_type(self):
        return "stop_order_buy"


class _StopOrderSell(_StopOrder):
    def __init__(self, trade_api, stop_order_id, trade_params):
        super().__init__(trade_api, stop_order_id, trade_params)

    def _check_stop_order(self):
        if self._last_price <= self._target_price:
            if self._last_price <= (self._target_price - self._trade_price_margin):
                self._cancel = True
            return True
        return False

    def _order(self):
        return self._trade_api.trade(currency_pair=self._currency_pair,
                               action='ask', price=self._last_price, amount=self._amount)

    def get_type(self):
        return "stop_order_sell"
