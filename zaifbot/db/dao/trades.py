from zaifbot.db.seed import Trades
from .base import DaoBase


class TradesDao(DaoBase):
    def _get_model(self):
        return Trades
