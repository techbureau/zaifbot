from sqlalchemy import and_
from zaifbot.modules.dao import DaoBase
from zaifbot.models.bollinger_bands import BollingerBands
from sqlalchemy import exc


class BollingerBandsDao(DaoBase):

    def __init__(self, currency_pair, period, length):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period
        self._length = length

    def get_model(self):
        return BollingerBands

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

    def create_data(self, bollinger_bands):
        session = self.get_session()
        try:
            for record in bollinger_bands:
                session.merge(record)
            session.commit()
            return True
        except exc.SQLAlchemyError:
            session.rollback()
        return False
