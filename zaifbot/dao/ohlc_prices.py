from sqlalchemy import and_
from sqlalchemy import exc
from zaifbot.common.bot_const import CLOSED
from zaifbot.common.logger import logger
from zaifbot.dao import DaoBase
from zaifbot.models.ohlc_prices import OhlcPrices


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
            for record in ohlc_prices:
                record['currency_pair'] = self._currency_pair
                record['period'] = self._period
                session.merge(OhlcPrices(**record))
            session.commit()
            session.close()
            return True
        except exc.SQLAlchemyError as e:
            logger.exception(e)
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
