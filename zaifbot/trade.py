from datetime import datetime
from zaifbot.common.action import Action, Buy, Sell
from zaifbot.currency_pairs import CurrencyPair
from zaifbot.dao.trades import TradesDao
from zaifbot.common.logger import trade_logger


class Trade:
    def __init__(self):
        self.currency_pair = None
        self.entry_datetime = None
        self.entry_price = None
        self.amount = None
        self.action = None
        self.exit_price = None
        self.exit_datetime = None
        self._dao = TradesDao
        self.id = None
        self.closed = False

    def entry(self, currency_pair, amount, entry_price, action):
        self.currency_pair = CurrencyPair(currency_pair)
        self.amount = amount
        self.entry_price = entry_price
        self.action = Action(action)
        self.entry_datetime = datetime.now()

        trade_obj = self._dao.create(currency_pair=str(self.currency_pair),
                                     amount=self.amount,
                                     entry_price=self.entry_price,
                                     action=str(self.action),
                                     entry_datetime=self.entry_datetime)
        self.id = trade_obj.id
        log_frame = "Entry: {{trade_id: {}, currency_pair: {}, action: {}," \
                    " amount: {}, entry_price: {}, entry_datetime: {}}}"
        trade_logger.info(log_frame.format(self.id, self.currency_pair, self.action,
                                           self.amount, self.entry_price, self.entry_datetime))

    def exit(self, exit_price):
        self.exit_price = exit_price
        self.exit_datetime = datetime.now()

        self._dao.update(exit_price=self.exit_price,
                         exit_datetime=self.exit_datetime,
                         profit=self.profit())

        log_frame = "Exit: {{trade_id: {}, currency_pair: {}, exit_price: {}, exit_datetime: {}}}"
        trade_logger.info(log_frame.format(self.id, self.currency_pair, self.exit_price, self.exit_datetime))

        self.closed = True

    def profit(self):
        if self.action == Buy:
            return self.exit_price - self.entry_price
        else:
            return self.entry_price - self.exit_price

    @property
    def is_short(self):
        return self.action == Sell

    @property
    def is_long(self):
        return self.action == Buy

    @property
    def is_closed(self):
        return self.closed

