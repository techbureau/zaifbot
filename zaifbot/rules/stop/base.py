from zaifbot.rules.rule import Rule


class Stop(Rule):
    def need_stop(self, trade):
        """
        :param trade: if having position, Trade class come in, else None
        """
        raise NotImplementedError
