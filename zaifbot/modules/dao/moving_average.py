from sqlalchemy import and_
from zaifbot.modules.dao import DaoBase
from zaifbot.models.moving_average import TradeLogs, MovingAverages
from sqlalchemy import exc
from zaifbot.bot_common.bot_const import CLOSED


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
            for index, record in trade_logs.iterrows():
                session.merge(TradeLogs(record.to_dict()))
            session.commit()
            session.close()
            return True
        except exc.SQLAlchemyError as e:
            print(e)
            session.rollback()
            session.close()
        return False

    def get_records(self, end_time, start_time, closed):
        session = self.get_session()
        select_query = session.query(self.model)
        if closed:
            select_query = select_query.filter(and_(self.model.time <= end_time,
                                                    self.model.time > start_time,
                                                    self.model.currency_pair == self._currency_pair,
                                                    self.model.period == self._period,
                                                    self.model.closed == CLOSED
                                                    ))
        else:
            select_query = select_query.filter(and_(self.model.time <= end_time,
                                                    self.model.time >= start_time,
                                                    self.model.currency_pair == self._currency_pair,
                                                    self.model.period == self._period
                                                    ))
        result = select_query.order_by(self.model.time).all()
        session.close()
        return result


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
                                                    self.model.closed == CLOSED
                                                    ))
        else:
            select_query = select_query.filter(and_(self.model.time <= end_time,
                                                    self.model.time > start_time,
                                                    self.model.currency_pair == self._currency_pair,
                                                    self.model.period == self._period,
                                                    self.model.length == self._length
                                                    ))
        result = select_query.order_by(self.model.time).all()
        session.close()
        return result

    def get_trade_logs_moving_average(self, end_time, start_time):
        session = self.get_session()
        result = session.query(TradeLogs, self.model)\
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
        session.close()
        return result

    def create_data(self, moving_average):
        session = self.get_session()
        for record in moving_average:
            session.merge(record)
        try:
            session.commit()
            session.close()
            return True
        except exc.SQLAlchemyError:
            session.rollback()
            session.close()
        return False
