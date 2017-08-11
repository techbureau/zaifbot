from datetime import datetime
from zaifbot.db.dao.trades import TradesDao
from zaifbot.exchange.action import Action, Buy, Sell
from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.logger import trade_logger
from zaifbot.exchange.api.http import BotTradeApi
from zaifbot.trade.tools import last_price


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
        self.entry_price = last_price(currency_pair=self.currency_pair)
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
        log_frame = "Entry: {{trade_id: {}, currency_pair: {}, action: {}," \
                    " amount: {}, entry_price: {}, entry_datetime: {}}}"
        trade_logger.info(log_frame.format(self.id_, self.currency_pair, self.action,
                                           self.amount, self.entry_price, self.entry_datetime),
                          extra={'strategy_ident': self._id_for_log()})

    def exit(self):
        self.exit_price = last_price(self.currency_pair)
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

        log_frame = "Exit: {{trade_id: {}, currency_pair: {}, exit_price: {}, exit_datetime: {}}}"
        trade_logger.info(log_frame.format(self.id_, self.currency_pair, self.exit_price, self.exit_datetime),
                          extra={'strategy_ident': self._id_for_log()})

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

    def _id_for_log(self):
        if self.strategy_name:
            return self.strategy_name
        if self.process_id:
            return self.process_id[:12]
        return ''
