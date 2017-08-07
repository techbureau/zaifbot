from zaifbot.db.dao.trades import TradesDao


class TradeHistory:
    def __init__(self):
        self._dao = TradesDao()
