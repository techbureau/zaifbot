from zaifbot.exchange.latest_price import get_latest_price
from zaifbot.rules.rule import Rule


class Exit(Rule):
    def __init__(self, *, mode='normal'):
        self._trade_api = None
        self._mode = mode

    def can_exit(self, trade):
        raise NotImplementedError

    def exit(self, trade):
        amount = trade.amount
        currency_pair = trade.currency_pair
        action = trade.action.opposite_action()
        price = get_latest_price(currency_pair)

        self._trade_api.trade(currency_pair=currency_pair,
                              amount=amount,
                              price=price,
                              action=action)

        trade.exit(price)
