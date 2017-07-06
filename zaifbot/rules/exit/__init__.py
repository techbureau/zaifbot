from zaifbot.rules.rule import Rule


class Exit(Rule):
    def __init__(self):
        self.trade_api = None

    def can_exit(self, trade):
        raise NotImplementedError

    def exit(self, trade):
       pass