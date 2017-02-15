from sqlalchemy import and_
from zaifbot.modules.dao import DaoBase
from zaifbot.models.moving_avarage.moving_average import TradeLogs, MovingAverage


class TradeLogsDao(DaoBase):

    def __init__(self, currency_pair, period):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period

    def get_model(self):
        return TradeLogs

    def get_record(self, end_time, start_time):
        session = self.get_session()
        return session.query(self.model).filter(and_(self.model.time <= end_time,
                                                     self.model.time >= start_time,
                                                     self.model.currency_pair == self._currency_pair,
                                                     self.model.period == self._period
                                                     )).order_by(self.model.time).all()

    def create_data(self, trade_logs):
        session = self.get_session()
        session.add_all(trade_logs)
        session.commit()


class MovingAverageDao(DaoBase):

    def __init__(self, currency_pair, period, length):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period
        self._length = length

    def get_model(self):
        return MovingAverage

    def get_record(self, end_time, start_time):
        session = self.get_session()
        return session.query(self.model).filter(and_(self.model.time <= end_time,
                                                     self.model.time >= start_time,
                                                     self.model.currency_pair == self._currency_pair,
                                                     self.model.period == self._period,
                                                     self.model.length == self._length)
                                                ).order_by(self.model.time).all()
