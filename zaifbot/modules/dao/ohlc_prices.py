from sqlalchemy import and_
from zaifbot.modules.dao import DaoBase
from zaifbot.models.ohlc_prices import OhlcPrices
from sqlalchemy import exc
from zaifbot.bot_common.bot_const import CLOSED


class OhlcPricesDao(DaoBase):

    def __init__(self, currency_pair, period):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period

    def get_model(self):
        return OhlcPrices

    def get_record(self, select_query):
        return select_query.order_by(self.model.time).all()

    def create_data(self, ohlc_prices):
        session = self.get_session()
        try:
            for index, record in ohlc_prices.iterrows():
                session.merge(OhlcPrices(**record.to_dict()))
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
