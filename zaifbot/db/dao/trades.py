from sqlalchemy import and_
from zaifbot.db.seed import Trades
from .base import DaoBase
from zaifbot.utils import is_float


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

            q = self.custom_filters(q, params)
            return q.all()

    def custom_filters(self, q, params):
        # todo: move to dao
        for key, value in params.items():
            operator, boundary = value.split()
            if is_float(boundary)is False:
                boundary = "'" + boundary + "'"
            source = "self._Model.{} {} {}".format(key, operator, boundary)
            q = q.filter(eval(source))
        return q
