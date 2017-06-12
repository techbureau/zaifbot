from zaifbot.models.order_log import OrderLogs
from zaifbot.modules.dao import DaoBase
from sqlalchemy import exc


class OrderLogsDao(DaoBase):
    def get_model(self):
        return OrderLogs

    def create_data(self, order_log):
        session = self.get_session()
        for record in order_log:
            session.merge(record)
        try:
            session.commit()
            session.close()
            return True
        except exc.SQLAlchemyError:
            session.rollback()
            session.close()
        return False
