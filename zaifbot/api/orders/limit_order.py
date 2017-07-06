from zaifbot.api.orders.common import OrderBase, log_before_trade
from zaifbot.common.bot_const import Action


class LimitOrder(OrderBase):
    def __init__(self, api, currency_pair, action, limit_price, amount, comment=''):
        super().__init__(api, currency_pair, comment)
        self._action = Action(action)
        self._limit_price = limit_price
        self._amount = amount

    @property
    def type(self):
        return 'LimitOrder'

    @property
    def info(self):
        self._info = super().info
        self._info['action'] = self._action
        self._info['amount'] = self._amount
        self._info['limit_price'] = self._limit_price
        return self._info

    @log_before_trade('order made')
    def make_order(self):
        result = self._api.trade(currency_pair=self._currency_pair,
                                 action=self._action,
                                 price=self._limit_price,
                                 amount=self._amount,
                                 comment=self._comment)
        self._info['zaif_order_id'] = result['order_id']
        return self
