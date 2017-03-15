from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price, ZaifOrder
from zaifbot.modules.processes.process_common import ProcessBase
from zaifbot.bollinger_bands import get_bollinger_bands
from time import time, sleep
from zaifbot.modules.dao.auto_trade import AutoTradeDao
from zaifbot.models.auto_trade import AutoTrade
from zaifbot.bot_common.bot_const import BUY, SELL
from operator import itemgetter


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
            auto_trade_record = self._auto_trade.get_record(self._start_time)
            self._buy_sell_flag = auto_trade_record[0].buy_sell_flag
            self._from_currency_amount = auto_trade_record[0].from_currency_amount
            self._to_currency_amount = auto_trade_record[0].to_currency_amount
        if self._buy_sell_flag == BUY\
                and self._last_price <= self._bollinger_bands['return']['bollinger_bands'][0]['sd2n']:
            print('\nbuy')
            print('current price:' + str(self._last_price))
            print('_bollinger band sd2n:' + str(self._bollinger_bands['return']['bollinger_bands'][0]['sd2n']))
            return True
        return True  # dbg

    def execute(self):
        zaif_order = ZaifOrder()
        active_orders = zaif_order.get_active_orders()
        if len(active_orders) == 0:
            return False
        sorted_active_orders = self._sort_active_orders(active_orders)
        trade_success = self._process_trade(zaif_order, sorted_active_orders)
        if self._continue is False and trade_success:
            return True
        else:
            return False

    def _process_trade(self, zaif_order, sorted_active_orders):
        from_currency_amount_after_trade = self._from_currency_amount
        to_currency_amount_after_trade = self._to_currency_amount
        failed_orders = []
        trade_success = False
        auto_trade_status = BUY
        for i in sorted_active_orders:
            amount = self._get_amount(i['price'], i['amount'], from_currency_amount_after_trade)
            trade_result = zaif_order.trade('ask', i['price'], amount)
            if trade_result['success']:
                from_currency_amount_after_trade -= i['price'] * trade_result['return']['received']
                to_currency_amount_after_trade += trade_result['return']['received']
            elif trade_result['return']['order_id']:
                failed_orders.append(trade_result['return']['order_id'])
            if from_currency_amount_after_trade <=\
                    self._last_price * MIN_CUR_AMOUNT[self.config.system.currency_pair]:
                trade_success = True
                break
        for i in failed_orders:
            zaif_order.cancel_order(i)
        if trade_success:
            auto_trade_status = SELL
        self._update_auto_trade_status(auto_trade_status, to_currency_amount_after_trade,
                                       from_currency_amount_after_trade)
        return trade_success

    def _sort_active_orders(self, active_orders):
        sorted_active_orders = []
        for k, v in active_orders.items():
            if v['action'] == 'bid' and v['currency_pair'] == self.config.system.currency_pair:
                sorted_active_orders.append({'price': v['price'], 'amount': v['amount']})
        sorted_active_orders.sort(key=itemgetter('price'))
        return sorted_active_orders

    def _get_amount(self, price, amount, from_currency_amount_after_trade):
        if (price * amount) >= from_currency_amount_after_trade:
            amount = from_currency_amount_after_trade / price
            amount = amount - (amount % MIN_CUR_AMOUNT[self.config.system.currency_pair])
            return amount
        else:
            amount = amount

    def _update_auto_trade_status(self, auto_trade_status, to_currency_amount_after_trade,
                                  from_currency_amount_after_trade):
        auto_trade_dataset = get_auto_trade_dataset(
            self._start_time,
            SELL,
            to_currency_amount_after_trade,
            from_currency_amount_after_trade
        )
        self._auto_trade.create_data(auto_trade_dataset)
