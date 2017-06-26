import time
from zaifbot.bot_common.bot_const import TRADE_ACTION
from uuid import uuid4
from abc import ABCMeta, abstractmethod
from threading import Thread, Event, Lock
from zaifbot.price.stream import ZaifLastPrice
from zaifbot.api.wrapper import BotTradeApi
from zaifbot.price.cache import ZaifCurrencyPairs
from zaifbot.bot_common.errors import ZaifBotError

class Order:
    def __init__(self, trade_api=None):
        self._api = trade_api or BotTradeApi()
        self._menu = _OrderMenu()
        self._active_orders = ActiveOrders(self._api)

    def market_order(self, currency_pair, action, amount, comment=''):
        order = self._menu.market_order(currency_pair, action, amount, comment).make_order(self._api)
        self._active_orders.add(order)
        return order.info

    def limit_order(self, currency_pair, action, limit_price, amount, comment=''):
        order = self._menu.limit_order(currency_pair, action, limit_price, amount, comment).make_order(self._api)
        self._active_orders.add(order)
        return order.info

    def stop_order(self, currency_pair, action, stop_price, amount, comment=''):
        order = self._menu.stop_order(currency_pair, action, stop_price, amount, comment).make_order(self._api)
        self._active_orders.add(order)
        return order.info

    def time_limit_cancel(self, order_id, wait_sec, *, is_remote=False):
        order = self._menu.time_limit_cancel(order_id, is_remote=is_remote).make_order(self._api, wait_sec)
        self._active_orders.add(order)
        return order.info

    def price_distance_cancel(self, order_id, currency_pair, distance, *, is_remote=False):
        order = self._menu.price_distance_cancel(order_id, currency_pair, is_remote=is_remote).make_order(self._api,
                                                                                                          distance)
        self._active_orders.add(order)
        return order.info

    def active_orders(self):
        return self._active_orders.all()

    def cancel(self, bot_order_id):
        return self._active_orders.find(bot_order_id).cancel(api=self._api)


class _Order(metaclass=ABCMeta):
    def __init__(self, comment):
        self._bot_order_id = str(uuid4())
        self._started_time = None
        self._comment = comment
        self._info = {}

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def info(self):
        self._info['bot_order_id'] = self._bot_order_id
        self._info['name'] = self.name
        self._info['comment'] = self._comment
        return self._info

    @abstractmethod
    def make_order(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def cancel(self, **kwargs):
        raise NotImplementedError

    @staticmethod
    def _is_token(currency_pair):
        currency_pairs = ZaifCurrencyPairs()
        record = currency_pairs[currency_pair]
        if record:
            return record['is_token']
        raise ZaifBotError('illegal currency_pair:{}'.format(currency_pair))


class _MarketOrder(_Order):
    def __init__(self, currency_pair, action, amount, comment=''):
        super().__init__(comment)
        self._currency_pair = currency_pair
        self._action = action
        self._amount = amount

    @property
    def name(self):
        return 'MarketOrder'

    @property
    def info(self):
        self._info['action'] = self._action
        self._info['currency_pair'] = self._currency_pair
        self._info['price'] = self._round_price()
        self._info['amount'] = self._amount
        return self._info

    def make_order(self, trade_api):
        trade_api.trade(currency_pair=self._currency_pair,
                        action=self._action,
                        price=self._round_price(),
                        amount=self._amount,
                        comment=self._comment)
        return self

    def _round_price(self):
        # todo: 中身の実装
        return ZaifLastPrice().last_price(self._currency_pair)['last_price']

    def cancel(self):
        pass


class _LimitOrder(_Order):
    def __init__(self, currency_pair, action, limit_price, amount, comment=''):
        super().__init__(comment)
        self._currency_pair = currency_pair
        self._action = action
        self._limit_price = limit_price
        self._amount = amount

    @property
    def name(self):
        return 'LimitOrder'

    @property
    def info(self):
        self._info = super().info
        self._info['currency_pair'] = self._currency_pair
        self._info['action'] = self._action
        self._info['amount'] = self._amount
        self._info['limit_price'] = self._limit_price
        return self._info

    def make_order(self, trade_api):
        result = trade_api.trade(currency_pair=self._currency_pair,
                                 action=self._action,
                                 price=self._limit_price,
                                 amount=self._amount,
                                 comment=self._comment)
        self._info['zaif_order_id'] = result['order_id']
        return self

    def cancel(self, *, api):
        is_token = self._is_token(self._currency_pair)
        order_id = self.info['zaif_order_id']
        return api.cancel_order(order_id=order_id, is_token=is_token)


_SLEEP_TIME = 1


class _OrderThreadRoutine(metaclass=ABCMeta):
    def _run(self, trade_api):
        while self._is_alive:
            self._every_time_before()
            if self._can_execute():
                self._before_execution()
                self._execute(trade_api)
                self._after_execution()
                self._stop()
            else:
                time.sleep(_SLEEP_TIME)

    @abstractmethod
    def _can_execute(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _execute(self, *args, **kwargs):
        raise NotImplementedError

    @property
    @abstractmethod
    def _is_alive(self):
        raise NotImplementedError

    @abstractmethod
    def _stop(self):
        raise NotImplementedError

    def _every_time_before(self):
        pass

    def _before_execution(self):
        pass

    def _after_execution(self):
        pass


class _StopOrder(_Order, _OrderThreadRoutine):
    def __init__(self, currency_pair, action, stop_price, amount, comment=''):
        super().__init__(comment)
        self._currency_pair = currency_pair
        self._action = action
        self._stop_price = stop_price
        self._amount = amount
        self._thread = None
        self._stop_event = Event()

    @property
    def name(self):
        return 'StopOrder'

    @property
    def info(self):
        info = super().info
        info['currency_pair'] = self._currency_pair
        info['action'] = self._action
        info['amount'] = self._amount
        info['stop_price'] = self._stop_price
        return info

    def make_order(self, trade_api):
        self._thread = Thread(target=self._run, args=(trade_api,), daemon=True)
        self._thread.start()
        return self

    def _execute(self, trade_api):
        return _MarketOrder(self._currency_pair, self._action, self._amount, self._comment).make_order(trade_api)

    def _can_execute(self):
        if self._action is TRADE_ACTION[0]:
            return self.__is_price_higher_than_stop_price()
        else:
            return self.__is_price_lower_than_stop_price()

    def __is_price_higher_than_stop_price(self):
        return ZaifLastPrice().last_price(self._currency_pair)['last_price'] > self._stop_price

    def __is_price_lower_than_stop_price(self):
        return ZaifLastPrice().last_price(self._currency_pair)['last_price'] < self._stop_price

    @property
    def _is_alive(self):
        return self._stop_event

    def _stop(self):
        self._stop_event.set()

    def cancel(self):
        self._stop()


class _AutoCancelOrder(_Order, _OrderThreadRoutine):
    def __init__(self, target_order_id, *, is_remote=False):
        super().__init__()
        self._target_order_id = target_order_id
        self._is_remote = is_remote
        self._stop_event = Event()

    @property
    def info(self):
        info = {
            'bot_order_id': self._bot_order_id,
            'name': self.name,
            'target_order_id': self._target_order_id
        }
        return info

    @abstractmethod
    def _can_execute(self, *args, **kwargs):
        raise NotImplementedError

    def _execute(self, order_id, trade_api):
        if self._is_remote:
            trade_api.cancel_order(order_id)
        else:
            pass

    def _is_alive(self):
        return self._stop_event

    def _stop(self):
        self._stop_event.set()

    def cancel(self):
        self._stop()


class _TimeLimitCancel(_AutoCancelOrder):
    def __init__(self, target_order_id, *, is_remote=False):
        super().__init__(target_order_id, is_remote=is_remote)
        self._start_time = None
        self._wait_sec = None

    @property
    def name(self):
        return 'AutoCancelByTime'

    @property
    def info(self):
        info = super().info
        info['wait_sec'] = self._wait_sec
        info['rest_sec'] = self._wait_sec - (int(time.time()) - self._start_time)
        return info

    def make_order(self, trade_api, wait_sec):
        self._wait_sec = wait_sec
        self._start_time = int(time.time())
        order = Thread(target=self._run, args=(trade_api,), daemon=True)
        order.start()
        return self

    def _can_execute(self):
        return self.__is_now_the_time()

    def __is_now_the_time(self):
        return (int(time.time()) - self._start_time) >= self._wait_sec


class _PriceDistanceCancel(_AutoCancelOrder):
    def __init__(self, target_order_id, currency_pair, *, is_remote=False):
        super().__init__(target_order_id, is_remote=is_remote)
        self._currency_pair = currency_pair
        self._start_price = ZaifLastPrice().last_price(self._currency_pair)['last_price']
        self._distance = None

    @property
    def name(self):
        return 'PriceDistanceCancel'

    @property
    def info(self):
        info = super().info
        info['start_price'] = self._start_price
        info['border_margin'] = self._distance
        return info

    def make_order(self, trade_api, distance):
        self._distance = distance
        order = Thread(target=self._run, args=(trade_api,), daemon=True)
        order.start()
        return self

    def _can_execute(self):
        return self.__is_price_beyond_the_boundary()

    def __is_price_beyond_the_boundary(self):
        last_price = ZaifLastPrice().last_price(self._currency_pair)['last_price']
        return abs(self._start_price - last_price) > self._distance


# 代替案求む。
class _OrderMenu:
    market_order = _MarketOrder
    stop_order = _StopOrder
    limit_order = _LimitOrder
    time_limit_cancel = _TimeLimitCancel
    price_distance_cancel = _PriceDistanceCancel


class ActiveOrders:
    _instance = None
    _lock = Lock()
    _thread = Thread()
    _active_orders = {}

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, api):
        self._api = api

    def is_found(self, order_id):
        pass

    def find(self, bot_order_id):
        # 失敗した時の挙動
        return self._active_orders[bot_order_id]

    def add(self, order):
        bot_order_id = order.info['bot_order_id']
        self._active_orders[bot_order_id] = order

    def all(self):
        return [order.info for order in self._active_orders.values()]

    def _update(self):
        with self._lock:
            remote_orders = self._api.active_orders()
            for active_order in self._active_orders:
                if active_order.info.get('zaif_order_id') not in remote_orders:
                    self._active_orders.pop(active_order.info.bot_order_id)
            for active_order in self._active_orders:
                if active_order.is_alive is False:
                    self._active_orders.pop(active_order.info.bot_order_id)
