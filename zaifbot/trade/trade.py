from datetime import datetime
from zaifbot.db.dao.trades import TradesDao
from zaifbot.exchange.action import Action, Buy, Sell
from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.logger import trade_logger
from zaifbot.exchange.api.http import BotTradeApi
from zaifbot.trade.tools import last_price
from zaifbot.exchange.tick import Tick


class Trade:
    def __init__(self):
        self.currency_pair = None
        self.entry_datetime = None
        self.entry_price = None
        self.amount = None
        self.action = None
        self.exit_price = None
        self.exit_datetime = None
        self.id_ = None
        self.closed = False
        self._trade_api = BotTradeApi()
        self._dao = TradesDao()
        self.strategy_name = None
        self.process_id = None

    def entry(self, currency_pair, amount, action):
        self.currency_pair = CurrencyPair(currency_pair)
        self.amount = amount
        self.entry_price = self._rounded_last_price()
        self.action = Action(action)
        self.entry_datetime = datetime.now()

        self._trade_api.trade(currency_pair=self.currency_pair,
                              amount=self.amount,
                              price=self.entry_price,
                              action=self.action)

        trade_obj = self._dao.create(currency_pair=self.currency_pair.name,
                                     amount=self.amount,
                                     entry_price=self.entry_price,
                                     action=self.action.name,
                                     strategy_name=self.strategy_name,
                                     process_id=self.process_id)

        self.id_ = trade_obj.id_
        self._logging_entry()

    def exit(self):
        self.exit_price = self._rounded_last_price()
        self.exit_datetime = datetime.now()

        self._trade_api.trade(currency_pair=self.currency_pair,
                              amount=self.amount,
                              price=self.exit_price,
                              action=self.action.opposite_action())

        self.closed = True

        self._dao.update(id_=self.id_,
                         exit_price=self.exit_price,
                         exit_datetime=self.exit_datetime,
                         profit=self.profit(),
                         closed=self.closed)

        self._logging_exit()

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

    def _logging_entry(self):
        log_frame = "Entry: {{trade_id: {}, currency_pair: {}, action: {}," \
                    " amount: {}, entry_price: {}, entry_datetime: {}}}"
        log_msg = log_frame.format(self.id_, self.currency_pair, self.action,
                                   self.amount, self.entry_price, self.entry_datetime)
        trade_logger.info(log_msg, extra={'strategyid': self._strategy_descriptor()})

    def _logging_exit(self):
        log_frame = "Exit: {{trade_id: {}, currency_pair: {}, exit_price: {}, exit_datetime: {}}}"
        log_msg = log_frame.format(self.id_, self.currency_pair, self.exit_price, self.exit_datetime)
        trade_logger.info(log_msg, extra={'strategyid': self._strategy_descriptor()})

    def _strategy_descriptor(self):
        return self.strategy_name or self.process_id[:12] or ''

    def _rounded_last_price(self):
        tick = Tick(self.currency_pair)
        price = last_price(self.currency_pair)
        return tick.truncate_price(price)
