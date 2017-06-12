from zaifbot.models.order_log import OrderLogs
from zaifbot.modules.dao import DaoBase
from sqlalchemy import exc
from zaifbot.bot_common.logger import logger


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
            logger.error(e, exc_info=True)
            session.rollback()
            session.close()
        return False
