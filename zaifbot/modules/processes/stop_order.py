from zaifbot.modules.utils import get_current_last_price
from time import sleep
from zaifbot.bot_common.bot_const import BUY, SELL, CANCEL, TRADE_ACTION
from zaifbot.modules.api.wrapper import BotTradeApi
from zaifbot.modules.utils import get_buyable_amount


class StopOrder:
    def __init__(self, trade_params):
        self._sleep_time = trade_params['sleep_time']
        self._api_key = trade_params['api_key']
        self._api_secret = trade_params['api_secret']
        self._target_price = trade_params['target_price']
        self._trade_status = trade_params['trade_status']
        self._trade_price_margin = trade_params['trade_price_margin']
        self._currency_pair = trade_params['currency_pair']
        self._amount = trade_params['amount']
        self._cancel_time = trade_params['cancel_time']

    def start_trade(self):
        while True:
            sleep(self._sleep_time)
            if self._is_started() is False:
                continue
            stop_process_flg = self._execute()
            if stop_process_flg:
                break

    def _is_started(self):
        current_last_price = get_current_last_price(self._currency_pair)
        if current_last_price is None:
            return False
        self._last_price = int(current_last_price['last_price'])
        return self._check_stop_order()

    def _execute(self):
        if self._trade_status == CANCEL:
            return True
        if self._trade_status == BUY:
            amount = get_buyable_amount(self._currency_pair,
                                        self._amount,
                                        self._last_price)
        else:
            amount = self._amount
        trade_api = BotTradeApi(self._api_key, self._api_secret)
        order = trade_api.trade(currency_pair=self._currency_pair,
                                action=TRADE_ACTION[self._trade_status],
                                price=self._last_price, amount=amount)
        if order['order_id'] is None:
            print(0)
            return False
        order_id = order['order_id']
        sleep(self._cancel_time)
        return self._check_order_result(order_id, trade_api)

    def _check_order_result(self, order_id, trade_api):
        active_orders = trade_api.active_orders(currency_pair=self._currency_pair)
        if 'order_id' in active_orders:
            print(1)
            trade_api.cancel_order(order_id)
            return False
        print(2)
        return True

    def _check_stop_order(self):
        if self._trade_status == BUY and self._last_price >= self._target_price:
            if self._last_price >= (self._target_price + self._trade_price_margin):
                self._trade_status = CANCEL
            return True
        elif self._trade_status == SELL and self._last_price <= self._target_price:
            if self._last_price <= (self._target_price - self._trade_price_margin):
                self._trade_status = CANCEL
            return True
        return False
