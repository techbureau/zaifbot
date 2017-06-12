from dao import DaoBase
from sqlalchemy import and_
from sqlalchemy import exc
from zaifbot.bot_common.bot_const import CLOSED
from zaifbot.models.moving_average import MovingAverages


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
