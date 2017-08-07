from sqlalchemy import and_
from zaifbot.db.seed import Trades
from .base import DaoBase


class TradesDao(DaoBase):
    def _get_model(self):
        return Trades

    def history(self, from_datetime, to_datetime, params=None):
        with self._session() as s:
            q = s.query(self._Model).filter(and_(
                    self._Model.entry_datetime >= from_datetime,
                    self._Model.exit_datetime <= to_datetime))

            if params is None:
                return q.all()

            if not isinstance(params, dict):
                raise TypeError("params should be 'dict'")

            q = self._custom_filters(q, params)
            return q.all()
