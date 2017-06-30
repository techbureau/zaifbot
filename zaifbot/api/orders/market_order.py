from zaifbot.api.orders.common import OrderBase
from zaifbot.common.bot_const import Action


class MarketOrder(OrderBase):
    def __init__(self, api, currency_pair, action, amount, comment=''):
        super().__init__(api, currency_pair, comment)
        self._action = Action(action)
        self._amount = amount

    @property
    def type(self):
        return 'MarketOrder'

    @property
    def info(self):
        self._info['action'] = self._action
        self._info['currency_pair'] = str(self._currency_pair)
        self._info['amount'] = self._amount
        return self._info

    def make_order(self):
        # todo: need refactoring
        is_buy = True if self.info['action'] == Action.Buy else False
        price = self._currency_pair.get_more_executable_price(self._currency_pair.last_price(), is_buy=is_buy)
        price_rounded = self._currency_pair.get_round_amount(price)
        self._api.trade(currency_pair=str(self._currency_pair),  # trade_apiでやりたい
                        action=self._action.value,  # trade_apiでやりたい
                        price=price_rounded,
                        amount=self._amount,
                        comment=self._comment)
        return self