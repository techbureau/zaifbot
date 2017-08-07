from zaifbot.db.dao.trades import TradesDao


class TradeResult:
    def __init__(self):
        self._dao = TradesDao()

    def history(self, from_datetime=None, to_datetime=None, filters=None):
        records = self._dao.history(from_datetime=from_datetime,
                                    to_datetime=to_datetime,
                                    filters=filters)

        return self._dao.rows2dicts(records)

    def gross_profit(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def gross_loss(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def profit(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def profit_factor(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def max_draw_down(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def long_trades_count(self):
        pass

    def short_trades_count(self):
        pass

    def win_trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def lose_trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def win_trades_percent(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def largest_win_trade(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def average_win_trade(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def largest_lose_trade(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def average_lose_trade(self, from_datetime=None, to_datetime=None, filters=None):
        pass

    def average_profit(self, from_datetime=None, to_datetime=None, filters=None):
        pass
