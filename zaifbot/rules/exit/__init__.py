from zaifbot.trade.tools import last_price
from zaifbot.rules.rule import Rule


class Exit(Rule):
    def can_exit(self, trade):
        raise NotImplementedError

    def exit(self, trade, trade_api):
        amount = trade.amount
        currency_pair = trade.currency_pair
        action = trade.action.opposite_action()
        price = last_price(currency_pair)

        trade_api.trade(currency_pair=currency_pair,
                        amount=amount,
                        price=price,
                        action=action)

        trade.exit(price)
