from zaifbot.rules.rule import Rule
from zaifbot.closing_price import latest_closing_price


class Exit(Rule):
    def __init__(self):
        self.trade_api = None

    def can_exit(self, trade):
        raise NotImplementedError

    def exit(self, trade):
        amount = trade.amount
        currency_pair = trade.currency_pair
        action = trade.action.opposite_action()
        price = latest_closing_price(currency_pair)

        self.trade_api.trade(currency_pair=currency_pair,
                             amount=amount,
                             price=price,
                             action=action)

        trade.exit(price)
