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
        win_trades = self.win_trades(from_datetime, to_datetime, filters)
        gross_profit = sum(win_trade['profit'] for win_trade in win_trades)
        return gross_profit

    def gross_loss(self, from_datetime=None, to_datetime=None, filters=None):
        lose_trades = self.lose_trades(from_datetime, to_datetime, filters)
        gross_loss = sum(lose_trade['profit'] for lose_trade in lose_trades)
        return gross_loss

    def profit(self, from_datetime=None, to_datetime=None, filters=None):
        gross_profit = self.gross_profit(from_datetime, to_datetime, filters)
        gross_loss = self.gross_loss(from_datetime, to_datetime, filters)
        # gross_loss is always negative value
        return gross_profit + gross_loss

    def profit_factor(self, from_datetime=None, to_datetime=None, filters=None):
        gross_profit = self.gross_profit(from_datetime, to_datetime, filters)
        gross_loss = self.gross_loss(from_datetime, to_datetime, filters)
        return gross_profit / gross_loss

    def trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        records = self.history(from_datetime, to_datetime, filters)
        return len(records)

    def long_trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        filters = filters or dict()
        filters['action'] = 'bid'

        return self.trades_count(from_datetime, to_datetime, filters)

    def short_trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        filters = filters or dict()
        filters['action'] = 'ask'

        return self.trades_count(from_datetime, to_datetime, filters)

    def win_trades(self, from_datetime=None, to_datetime=None, filters=None):
        filters = filters or dict()
        filters['profit'] = '>, 0'
        return self.history(from_datetime, to_datetime, filters)

    def lose_trades(self, from_datetime=None, to_datetime=None, filters=None):
        filters = filters or dict()
        filters['profit'] = '<, 0'
        return self.history(from_datetime, to_datetime, filters)

    def win_trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        win_trades = self.win_trades(from_datetime, to_datetime, filters)
        return len(win_trades)

    def lose_trades_count(self, from_datetime=None, to_datetime=None, filters=None):
        lose_trades = self.lose_trades(from_datetime, to_datetime, filters)
        return len(lose_trades)

    def win_trades_percent(self, from_datetime=None, to_datetime=None, filters=None):
        trades_count = self.trades_count(from_datetime, to_datetime, filters)
        win_trades_count = self.win_trades_count(from_datetime, to_datetime, filters)

        return (win_trades_count / trades_count) * 100

    def lose_trades_percent(self, from_datetime=None, to_datetime=None, filters=None):
        trades_count = self.trades_count(from_datetime, to_datetime, filters)
        lose_trades_count = self.lose_trades_count(from_datetime, to_datetime, filters)

        return (lose_trades_count / trades_count) * 100

    def largest_win_trade(self, from_datetime=None, to_datetime=None, filters=None):
        win_trades = self.win_trades(from_datetime, to_datetime, filters)
        return max(win_trades, key=lambda x: x['profit'])

    def largest_win_profit(self, from_datetime=None, to_datetime=None, filters=None):
        return self.largest_win_trade(from_datetime, to_datetime, filters)['profit']

    def average_win_profit(self, from_datetime=None, to_datetime=None, filters=None):
        gross_profit = self.gross_profit(from_datetime, to_datetime, filters)
        win_trades_count = self.win_trades_count(from_datetime, to_datetime, filters)
        return gross_profit / win_trades_count

    def largest_lose_trade(self, from_datetime=None, to_datetime=None, filters=None):
        lose_trades = self.lose_trades(from_datetime, to_datetime, filters)
        return min(lose_trades, key=lambda x: x['profit'])

    def largest_lose_loss(self, from_datetime=None, to_datetime=None, filters=None):
        return self.largest_lose_trade(from_datetime, to_datetime, filters)['profit']

    def average_lose_profit(self, from_datetime=None, to_datetime=None, filters=None):
        gross_loss = self.gross_loss(from_datetime, to_datetime, filters)
        lose_trades_count = self.lose_trades_count(from_datetime, to_datetime, filters)
        return gross_loss / lose_trades_count

    def average_profit(self, from_datetime=None, to_datetime=None, filters=None):
        profit = self.profit(from_datetime, to_datetime, filters)
        trades_count = self.trades_count(from_datetime, to_datetime, filters)
        return profit / trades_count
