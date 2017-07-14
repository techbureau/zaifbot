from zaifbot.api_manage import APIRepository
from zaifbot.rules.rule import Rule
from zaifbot.trade import Trade
from zaifbot.exchange.action import Action
from zaifbot.logger import trade_logger


class Entry(Rule):
    def __init__(self, amount, action='bid'):
        self.currency_pair = None
        self._trade_api = APIRepository().trade_api
        self._amount = amount
        self._action = Action(action)

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self):
        price = self.currency_pair.last_price()
        self._trade_api.trade(currency_pair=self.currency_pair,
                              amount=self._amount,
                              price=price,
                              action=self._action)
        trade_logger.info('entry')
        trade = Trade()
        trade.entry(currency_pair=self.currency_pair,
                    amount=self._amount,
                    entry_price=price,
                    action=self._action)

        return trade
