from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.processes.process_common import ProcessBase
from zaifbot.bollinger_bands import get_bollinger_bands
from time import time
from zaifbot.modules.dao.auto_trade import AutoTradeDao
from zaifbot.models.auto_trade import AutoTrade
from zaifbot.bot_common.bot_const import BUY, SELL


def get_auto_trade_dataset(
        start_time, buy_sell_flag, to_currency_amount, from_currency_amount):
    return AutoTrade(
        start_time=start_time,
        buy_sell_flag=buy_sell_flag,
        to_currency_amount=to_currency_amount,
        from_currency_amount=from_currency_amount
    )


class BuyByPrice(ProcessBase):
    def get_name(self):
        return 'buy_by_price'

    def is_started(self):
        last_price = get_current_last_price()
        if last_price <= self.config.event.buy.target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError


class BuyByBollingerBands(ProcessBase):
    def __init__(
            self, length, from_currency_amount, buy_sell_flag=BUY, continue_=False, start_time=None):
        super().__init__()
        self._length = length
        self._continue = continue_
        self._buy_sell_flag = buy_sell_flag
        self._from_currency_amount = from_currency_amount
        self._start_time = start_time
        self._auto_trade = AutoTradeDao(self._start_time)
        if continue_ and buy_sell_flag == BUY:
            self._auto_trade_record = []
            auto_trade_dataset = get_auto_trade_dataset(
                self._start_time,
                self._buy_sell_flag,
                0.0,
                self._from_currency_amount
            )
            self._auto_trade.create_data(auto_trade_dataset)

    def get_name(self):
        return 'buy_by_bolinger_bands'

    def is_started(self):
        self._last_price = get_current_last_price()
        self._bollinger_bands = get_bollinger_bands(
            self.config.system.currency_pair,
            self.config.system.sleep_time,
            1,
            int(time()),
            self._length
        )
        if self._bollinger_bands['success'] == 0:
            return False
        if self._continue:
            self._auto_trade_record = self._auto_trade.get_record(self._start_time)
            self._buy_sell_flag = self._auto_trade_record[0].buy_sell_flag
        if self._buy_sell_flag == BUY\
                and self._last_price <= self._bollinger_bands['return']['bollinger_bands'][0]['sd2n']:
            print('\nbuy')
            print('current price:' + str(self._last_price))
            print('_bollinger band sd2n:' + str(self._bollinger_bands['return']['bollinger_bands'][0]['sd2n']))
            return True
        return False

    def execute(self):
        # implement trade order here
        if self._continue:
            auto_trade_dataset = get_auto_trade_dataset(
                self._start_time,
                SELL,
                0.0,
                0.0
            )
            self._auto_trade.create_data(auto_trade_dataset)
            return False
        else:
            return True
