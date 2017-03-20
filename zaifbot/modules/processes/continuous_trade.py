from zaifbot.bot_common.utils import get_current_last_price, ZaifOrder
from zaifbot.modules.processes.process_common import ProcessBase
from zaifbot.bollinger_bands import get_bollinger_bands
from time import time
from zaifbot.bot_common.bot_const import *


class ContinuousTrade(ProcessBase):
    def __init__(self, sell_type, start_status,
                 start_currency_amount, length=20, last_bought_price=0.0):
        super().__init__()
        self._length = length
        self._sell_type = sell_type
        self._trade_status = start_status
        self._from_currency_amount = 0.0
        self._to_currency_amount = 0.0
        self._last_bought_price = last_bought_price
        if self._trade_status == BUY:
            self._from_currency_amount = start_currency_amount
        else:
            self._to_currency_amount = start_currency_amount

    def get_name(self):
        return 'continuous_trade'

    def is_started(self):
        self._last_price = self._round_last_price(get_current_last_price())
        if self._check_stop_loss():
            return True
        target_price = self._get_target_price()
        if target_price['success'] is False:
            return False
        if self._trade_status == BUY and self._last_price <= target_price['price']:
            return True
        elif self._trade_status == SELL and self._last_price >= target_price['price']:
            return True
        return False

    def execute(self):
        if self._trade_status == STOP_LOSS:
            return True
        zaif_order = ZaifOrder()
        amount = self._get_amount()
        trade_result = zaif_order.trade(TRADE_ACTION[self._trade_status], self._last_price, amount)
        if trade_result['success']:
            self._update_currency_amounts(self._last_price, trade_result['return']['received'])
        elif trade_result['return']['order_id']:
            zaif_order.cancel_order(trade_result['return']['order_id'])
        if self._check_trade_finish:
            self._update_auto_trade_status()
        return False

    def _get_target_price(self):
        if self._trade_status == BUY:
            bollinger_bands = get_bollinger_bands(self.config.system.currency_pair,
                                                  self.config.system.sleep_time, 1,
                                                  int(time()), self._length)
            if bollinger_bands['success'] == 0:
                return {'success': False}
            target_price = bollinger_bands['return']['bollinger_bands'][0]['sd2n']
            return {'success': True, 'price': target_price}
        elif self._sell_type == 'BB':
            bollinger_bands = get_bollinger_bands(self.config.system.currency_pair,
                                                  self.config.system.sleep_time, 1,
                                                  int(time()), self._length)
            if bollinger_bands['success'] == 0:
                return {'success': False}
            target_price = bollinger_bands['return']['bollinger_bands'][0]['sd2p']
            return {'success': True, 'price': target_price}
        else:
            return {'success': True,
                    'price': self._last_bought_price * float(self._sell_type)}

    def _get_amount(self):
        if self._trade_status == BUY:
            amount = self._from_currency_amount / self._last_price
            amount = amount - (amount % MIN_AMOUNT_STEP[self.config.system.currency_pair])
            return amount
        amount = self._to_currency_amount
        amount = amount - (amount % MIN_AMOUNT_STEP[self.config.system.currency_pair])
        return amount

    def _update_currency_amounts(self, price, amount):
        if self._trade_status == BUY:
            self._from_currency_amount -= price * amount
            self._to_currency_amount += amount
            self._last_bought_price = self._last_price
        else:
            self._from_currency_amount += price * amount
            self._to_currency_amount -= amount

    def _check_trade_finish(self):
        if (self._trade_status == BUY and
                self._from_currency_amount <=
                self._last_price * MIN_AMOUNT_STEP[self.config.system.currency_pair]) or\
                (self._trade_status == SELL and
                    self._to_currency_amount <=
                    MIN_AMOUNT_STEP[self.config.system.currency_pair]):
            return True
        return False

    def _update_auto_trade_status(self):
        if self._trade_status == BUY:
            self._trade_status = SELL
        else:
            self._trade_status = BUY

    def _round_last_price(self, last_price):
        if self._trade_status == BUY:
            return last_price + (
                (last_price + MIN_PRICE_STEP[self.config.system.currency_pair])
                % MIN_PRICE_STEP[self.config.system.currency_pair])
        else:
            return last_price - (last_price % MIN_PRICE_STEP[self.config.system.currency_pair])

    def _check_stop_loss(self):
        if self._trade_status == SELL:
            bollinger_bands = get_bollinger_bands(self.config.system.currency_pair,
                                                  self.config.system.sleep_time, 1,
                                                  int(time()), self._length)
            if bollinger_bands['return']['bollinger_bands'][0]['sd3n'] > self._last_price:
                self._trade_status = STOP_LOSS
                return True
        return False
