from zaifbot.rules.rule import Rule


class Exit(Rule):
    def __init__(self, name):
        self.name = name or self.__class__.__name__

    def can_exit(self, trade):
        raise NotImplementedError

    @staticmethod
    def exit(trade):
        trade.exit()
