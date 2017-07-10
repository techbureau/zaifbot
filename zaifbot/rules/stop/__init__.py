from zaifbot.rules.rule import Rule


class Stop(Rule):
    def need_stop(self, trade):
        raise NotImplementedError
