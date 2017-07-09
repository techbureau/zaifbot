from sqlalchemy import exc
from zaifbot.common.logger import bot_logger
from zaifbot.dao import DaoBase
from zaifbot.models.trades import Trades


class TradesDao(DaoBase):
    def get_model(self):
        return Trades

    def create_data(self, order_log):
        session = self.get_session()
        session.merge(Trades(**order_log))
        try:
            session.commit()
            session.close()
            return True
        except exc.SQLAlchemyError as e:
            bot_logger.exception(e)
            session.rollback()
            session.close()
        return False
