from zaifbot.rules.rule import Rule


class Exit(Rule):
    def can_exit(self, trade):
        raise NotImplementedError

    @staticmethod
    def exit(trade):
        trade.exit()
