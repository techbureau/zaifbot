from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price, ZaifOrder
from zaifbot.modules.processes.process_common import ProcessBase
from zaifbot.bollinger_bands import get_bollinger_bands
from time import time, sleep
from zaifbot.modules.dao.auto_trade import AutoTradeDao
from zaifbot.models.auto_trade import AutoTrade
from zaifbot.bot_common.bot_const import BUY, SELL, MIN_TO_CUR_AMOUNT, TRADE_ACTION
from operator import itemgetter


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
        self._last_price = get_current_last_price()
        target_price = self._get_target_price()
        if target_price['success'] is False:
            return False
        if self._trade_status == BUY and self._last_price <= target_price['price']:
            print('--- buy ---')
            print('current_price:' + str(self._last_price))
            print('target_price:' + str(target_price['price']))
            return True
        elif self._trade_status == SELL and self._last_price >= target_price['price']:
            print('--- sell ---')
            print('current_price:' + str(self._last_price))
            print('target_price:' + str(target_price['price']))
            return True
        return False

    def execute(self):
        zaif_order = ZaifOrder()
        active_orders = zaif_order.get_active_orders()
        if len(active_orders) == 0:
            return False
        sorted_active_orders = self._sort_active_orders(active_orders)
        self._process_trade(zaif_order, sorted_active_orders)
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

    def _sort_active_orders(self, active_orders):
        sorted_active_orders = []
        for k, v in active_orders.items():
            if v['action'] == 'ask' and v['currency_pair'] == self.config.system.currency_pair\
                    and self._trade_status  == BUY:
                sorted_active_orders.append({'price': v['price'], 'amount': v['amount']})
            elif v['action'] == 'bid' and v['currency_pair'] == self.config.system.currency_pair\
                    and self._trade_status == SELL and v['price'] >= self._last_bought_price:
                sorted_active_orders.append({'price': v['price'], 'amount': v['amount']})
        if self._trade_status == BUY:
            sorted_active_orders.sort(key=itemgetter('price'))
        else:
            sorted_active_orders.sort(key=itemgetter('price'), reverse=True)
        return sorted_active_orders

    def _process_trade(self, zaif_order, sorted_active_orders):
        from_currency_amount_after_trade = self._from_currency_amount
        to_currency_amount_after_trade = self._to_currency_amount
        failed_orders = []
        trade_finish = False
        for i in sorted_active_orders:
            amount = self._get_amount(i['price'], i['amount'])
            trade_result = zaif_order.trade(TRADE_ACTION[self._trade_status], i['price'], amount)
            if trade_result['success']:
                self._update_currency_amounts(i['price'], trade_result['return']['received'])
            elif trade_result['return']['order_id']:
                failed_orders.append(trade_result['return']['order_id'])
            if self._check_trade_finish:
                trade_finish = True
                break
        self._cancel_failed_orders(failed_orders, zaif_order)
        if trade_finish:
            self._update_auto_trade_status()

    def _get_amount(self, price, amount):
        if (price * amount) >= self._from_currency_amount and self._trade_status == BUY:
            amount = self._from_currency_amount / price
            amount = amount - (amount % MIN_TO_CUR_AMOUNT[self.config.system.currency_pair])
            return amount
        elif amount >= self._to_currency_amount and self._trade_status == SELL:
            amount = self._to_currency_amount
            amount = amount - (amount % MIN_TO_CUR_AMOUNT[self.config.system.currency_pair])
        else:
            amount = amount

    def _update_currency_amounts(self, price, amount):
        if self._trade_status == BUY:
            self._from_currency_amount -= price * amount
            self._to_currency_amount += amount
            self._last_bought_price = self._last_price
        self._from_currency_amount += price * amount
        self._to_currency_amount -= amount

    def _cancel_failed_orders(self, failed_orders, zaif_order):
        for i in failed_orders:
            zaif_order.cancel_order(i)

    def _check_trade_finish(self):
        if (self._trade_status == BUY and
                self._from_currency_amount <=
                self._last_price * MIN_TO_CUR_AMOUNT[self.config.system.currency_pair]) or\
                (self._trade_status == SELL and
                    self._to_currency_amount <=
                    MIN_TO_CUR_AMOUNT[self.config.system.currency_pair]):
            return True
        return False

    def _update_auto_trade_status(self):
        if self._trade_status == BUY:
            self._trade_status = SELL
        else:
            self._trade_status = BUY
