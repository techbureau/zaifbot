from zaifbot.db.dao.trades import TradesDao


class TradeResult:
    def __init__(self):
        self._dao = TradesDao()

    def history(self, from_datetime, to_datetime, params=None):
        records = self._dao.history(from_datetime=from_datetime,
                                    to_datetime=to_datetime,
                                    params=params)

        return self._dao.rows2dicts(records)
