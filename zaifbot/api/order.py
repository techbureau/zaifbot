import time
from zaifbot.bot_common.bot_const import TRADE_ACTION
from uuid import uuid4
from abc import ABCMeta, abstractmethod
from threading import Thread, Event
from zaifbot.price.stream import ZaifLastPrice
from zaifbot.api.wrapper import BotTradeApi
from zaifbot.price.cache import ZaifCurrencyPairs
from zaifbot.bot_common.errors import ZaifBotError


__all__ = ['Order']


class Order:
    def __init__(self, trade_api=None):
        self._api = trade_api or BotTradeApi()
        self._menu = _OrderMenu()

    def market_order(self, currency_pair, action, amount, comment=''):
        order = self._menu.market_order(currency_pair, action, amount, comment).make_order(self._api)
        return order.info

    def limit_order(self, currency_pair, action, limit_price, amount, comment=''):
        order = self._menu.limit_order(currency_pair, action, limit_price, amount, comment).make_order(self._api)
        return order.info

    def stop_order(self, currency_pair, action, stop_price, amount, comment=''):
        order = self._menu.stop_order(currency_pair, action, stop_price, amount, comment).make_order(self._api)
        return order.info


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


_SLEEP_TIME = 1


class _OrderThreadRoutine(metaclass=ABCMeta):
    def _run(self, trade_api):
        while self.is_alive:
            self._every_time_before()
            if self._can_execute():
                self._before_execution()
                self._execute(trade_api)
                self._after_execution()
                self.stop()
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
    def is_alive(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
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
        self._info = super().info
        self._info['currency_pair'] = self._currency_pair
        self._info['action'] = self._action
        self._info['amount'] = self._amount
        self._info['stop_price'] = self._stop_price
        return self._info

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
    def is_alive(self):
        return not self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()


# 果たしてこれでよいのか
class _OrderMenu:
    market_order = _MarketOrder
    stop_order = _StopOrder
    limit_order = _LimitOrder
