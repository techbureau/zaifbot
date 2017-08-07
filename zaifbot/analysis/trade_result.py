from zaifbot.db.dao.trades import TradesDao


class TradeResult:
    def __init__(self):
        self._dao = TradesDao()

    def history(self, from_datetime, to_datetime, filters=None):
        records = self._dao.history(from_datetime=from_datetime,
                                    to_datetime=to_datetime,
                                    filters=filters)

        return self._dao.rows2dicts(records)

    def most_profitable_trade(self):
        pass

    def least_profitable_trade(self):
        pass

    def profit_for_a_period(self, from_datetime, to_datetime, filters=None):
        pass

    def profit_of_a_strategy(self, name, params):
        pass
