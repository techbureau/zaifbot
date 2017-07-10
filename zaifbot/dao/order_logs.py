from zaifbot.models import OrderLogs
from .base import DaoBase


class OrderLogsDao(DaoBase):
    def _get_model(self):
        return OrderLogs
