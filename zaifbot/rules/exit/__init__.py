from zaifbot.rules.rule import Rule


class Exit(Rule):
    def __init__(self):
        self.trade_api = None
        self._amount = None
        self._currency_pair = None
        self._action = None

    def can_exit(self, trade):
        raise NotImplementedError

    def exit(self, trade):
        self._amount = trade.amount
        self._currency_pair = trade.currency_pair
        self._action = trade.action.get_opposite_action()

        price = self._currency_pair.last_price()
        self.trade_api.trade(currency_pair=self._currency_pair,
                             amount=self._amount,
                             price=price,
                             action=self._action)
        trade.update(exit_price=price)
        return True
