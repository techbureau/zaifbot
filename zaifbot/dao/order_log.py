from sqlalchemy import exc
from zaifbot.common.logger import bot_logger
from zaifbot.dao import DaoBase
from zaifbot.models.order_log import OrderLogs


class OrderLogsDao(DaoBase):
    def get_model(self):
        return OrderLogs

    def create_data(self, order_log):
        session = self.get_session()
        session.merge(OrderLogs(**order_log))
        try:
            session.commit()
            session.close()
            return True
        except exc.SQLAlchemyError as e:
            bot_logger.exception(e)
            session.rollback()
            session.close()
        return False
