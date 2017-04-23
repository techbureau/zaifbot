from zaifbot.bot_common.utils import get_current_last_price, ZaifOrder
from zaifbot.modules.processes.process_common import ProcessBase
from zaifbot.bollinger_bands import get_bollinger_bands
from time import time
from zaifbot.bot_common.bot_const import *
from zaifbot.bot_common.save_trade_log import save_trade_log


class ContinuousTrade(ProcessBase):
    def __init__(self, currency_pair, from_currency_amount, api_key, api_secret,
                 limit_diff=100, stop_loss_limit=50, length=20, sleep_time='1m'):
        super().__init__()
        self._api_key = api_key
        self._api_secret = api_secret
        self._length = length
        self._stop_loss = False
        self._stop_loss_limit = stop_loss_limit
        self._limit_diff = limit_diff
        self._from_currency_amount = from_currency_amount
        self._currency_pair = currency_pair
        self._sleep_time = sleep_time
        self.trade_log_name =\
            "./trade_history_{0}_{1}_{2}_{3}_{4}.log".format(int(time()), self._currency_pair,
                                                             self._from_currency_amount,
                                                             self._sleep_time, stop_loss_limit)

    def get_name(self):
        return 'continuous_trade'

    def is_started(self):
        current_last_price = get_current_last_price(self._currency_pair)
        self._last_price =\
            int(self._round_last_price(current_last_price['last_price'], self._currency_pair))
        zaif_order = ZaifOrder(self._api_key, self._api_secret)
        if len(zaif_order.get_active_orders(self._currency_pair)):
            last_trade_history = zaif_order.get_last_trade_history(self._currency_pair)
            last_trade_values = list(last_trade_history.values())[0]
            if self._check_stop_loss(last_trade_values):
                zaif_order.trade('ask', self._last_price, last_trade_values['amount'])
                return True
            return False
        target_price = self._get_target_price(self._currency_pair)
        if target_price['success'] is False:
            return False
        if self._last_price <= target_price['price']:
            return True
        return False

    def execute(self):
        if self._stop_loss:
            print('stop loss!')
            return True
        zaif_order = ZaifOrder(self._api_key, self._api_secret)
        amount = self._get_amount(self._currency_pair)
        limit = self._last_price + self._limit_diff
        zaif_order.trade(self._currency_pair, 'bid', self._last_price, amount, limit)
        save_trade_log(self.trade_log_name, int(time()), 'bid', self._last_price, amount, limit)

        return False

    def _get_target_price(self, currency_pair):
        bollinger_bands = get_bollinger_bands(currency_pair,
                                              self._sleep_time, 1,
                                              int(time()), self._length)
        if bollinger_bands['success'] == 0:
            return {'success': False}
        target_price = bollinger_bands['return']['bollinger_bands'][0]['sd2n']
        return {'success': True, 'price': target_price}

    def _get_amount(self, currency_pair):
        amount = self._from_currency_amount / self._last_price
        amount = amount - (amount % MIN_AMOUNT_STEP[currency_pair])
        return amount

    def _round_last_price(self, last_price, currency_pair):
        return last_price + (
            (last_price + MIN_PRICE_STEP[currency_pair])
            % MIN_PRICE_STEP[currency_pair])

    def _check_stop_loss(self, last_trade_values):
        if last_trade_values['your_action'] == 'bid'\
                and self._last_price <= last_trade_values['price'] - self._stop_loss_limit:
            self._stop_loss = True
            return True
        return False
