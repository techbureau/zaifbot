from zaifbot.rules.entry import Entry
from zaifbot.rules.exit import Exit
from zaifbot.exchange.action import Action


class BTEntry(Entry):
    def __init__(self, amount, action='bid'):
        self.currency_pair = None
        self._trade_api = None
        self._amount = amount
        self._action = Action(action)
        self._mode = mode

    def can_entry(self, *args, **kwargs):
        raise NotImplementedError

    def entry(self):
        pass
        return None



class BTExit(Exit):
    pass


def BT_last_price():
    pass
