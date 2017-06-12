from zaifbot.models.order_log import OrderLogs
from zaifbot.modules.dao import DaoBase


class OrderLogsDao(DaoBase):
    def get_model(self):
        return OrderLogs
