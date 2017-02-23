from sqlalchemy import and_
from zaifbot.modules.dao import DaoBase
from zaifbot.models.moving_average import TradeLogs, MovingAverages
from sqlalchemy import exc


class TradeLogsDao(DaoBase):

    def __init__(self, currency_pair, period):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period

    def get_model(self):
        return TradeLogs

    def get_record(self, select_query):
        return select_query.order_by(self.model.time).all()

    def create_data(self, trade_logs):
        session = self.get_session()
        try:
            for record in trade_logs:
                session.merge(record)
            session.commit()
            return True
        except exc.SQLAlchemyError:
            session.rollback()
        return False

    def get_records(self, end_time, start_time, closed):
        session = self.get_session()
        select_query = session.query(self.model)
        if closed:
            select_query = select_query.filter(and_(self.model.time <= end_time,
                                                    self.model.time > start_time,
                                                    self.model.currency_pair == self._currency_pair,
                                                    self.model.period == self._period,
                                                    self.model.closed == 1
                                                    ))
        else:
            select_query = select_query.filter(and_(self.model.time <= end_time,
                                                    self.model.time >= start_time,
                                                    self.model.currency_pair == self._currency_pair,
                                                    self.model.period == self._period
                                                    ))
        return select_query.order_by(self.model.time).all()


class MovingAverageDao(DaoBase):

    def __init__(self, currency_pair, period, length):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period
        self._length = length

    def get_model(self):
        return MovingAverages

    def get_records(self, end_time, start_time, closed):
        session = self.get_session()
        select_query = session.query(self.model)
        if closed:
            select_query = select_query.filter(and_(self.model.time <= end_time,
                                                    self.model.time > start_time,
                                                    self.model.currency_pair == self._currency_pair,
                                                    self.model.period == self._period,
                                                    self.model.length == self._length,
                                                    self.model.closed == 1
                                                    ))
        else:
            select_query = select_query.filter(and_(self.model.time <= end_time,
                                                    self.model.time > start_time,
                                                    self.model.currency_pair == self._currency_pair,
                                                    self.model.period == self._period,
                                                    self.model.length == self._length
                                                    ))
        return select_query.order_by(self.model.time).all()

    def get_trade_logs_moving_average(self, end_time, start_time):
        session = self.get_session()
        return session.query(TradeLogs, self.model)\
            .outerjoin(self.model, and_(
                TradeLogs.time == self.model.time,
                TradeLogs.currency_pair == self.model.currency_pair,
                TradeLogs.period == self.model.period,
                self.model.length == self._length))\
            .filter(and_(TradeLogs.time <= end_time,
                         TradeLogs.time > start_time,
                         TradeLogs.currency_pair == self._currency_pair,
                         TradeLogs.period == self._period)
                    ).order_by(TradeLogs.time).all()

    def create_data(self, moving_average):
        session = self.get_session()
        for record in moving_average:
            session.merge(record)
        try:
            session.commit()
            return True
        except exc.SQLAlchemyError:
            session.rollback()
        return False
