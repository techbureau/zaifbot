from zaifbot.modules.dao import DaoBase
from zaifbot.models.auto_trade import AutoTrade
from sqlalchemy import exc


class AutoTradeDao(DaoBase):

    def __init__(self, start_time):
        super().__init__()
        self._start_time = start_time

    def get_model(self):
        return AutoTrade

    def get_record(self, start_time):
        session = self.get_session()
        result = session.query(self.model).filter(self.model.start_time == start_time).all()
        session.close()
        return result

    def create_data(self, auto_trade_data):
        session = self.get_session()
        try:
            session.merge(auto_trade_data)
            session.commit()
            session.close()
            return True
        except exc.SQLAlchemyError:
            session.rollback()
            session.close()
        return False
