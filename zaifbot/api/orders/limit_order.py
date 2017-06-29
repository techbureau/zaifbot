from zaifbot.api.orders.common import OrderBase


class LimitOrder(OrderBase):
    def __init__(self, currency_pair, action, limit_price, amount, comment=''):
        super().__init__(currency_pair, comment)
        self._action = action
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

    def make_order(self, trade_api):
        # tradeの方でstrにするようにする。
        result = trade_api.trade(currency_pair=str(self._currency_pair),
                                 action=self._action,
                                 price=self._limit_price,
                                 amount=self._amount,
                                 comment=self._comment)
        self._info['zaif_order_id'] = result['order_id']
        return self
