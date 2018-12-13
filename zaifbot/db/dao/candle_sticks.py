from sqlalchemy import and_

from zaifbot.db.seed import CandleSticks
from .base import DaoBase
from zaifbot.utils.utils import merge_dict, random_sleep
from zaifbot.exchange.api.http import BotChartApi


class CandleSticksDao(DaoBase):
    def __init__(self, currency_pair, period):
        super().__init__()
        self._currency_pair = str(currency_pair)
        self._period = str(period)

    def _get_model(self):
        return CandleSticks

    def get_by_duration(self, count, start_time, end_time, *, closed=False):
        db_records = self._get_by_duration_db(start_time, end_time, closed=closed)
        db_records_dict = self.rows2dicts(db_records)
        if len(db_records_dict) >= count:
            return db_records

        api_records = self._get_by_duration_web(count, start_time, end_time)
        return api_records

    def _get_by_duration_web(self, count, start_time, to_epoch_time):
        chart_api = BotChartApi()
        records = chart_api.history(self._currency_pair, self._period, start_time, to_epoch_time)

        while len(records) < count:
            random_sleep(1, 2)
            records = chart_api.history(self._currency_pair, self._period, start_time, to_epoch_time)

        self._save_records(records)
        return records

    def _get_by_duration_db(self, start_time, end_time, *, closed=False):
        with self._session() as s:
            result = s.query(self._Model).filter(
                and_(self._Model.time <= end_time,
                     self._Model.time >= start_time,
                     self._Model.currency_pair == self._currency_pair,
                     self._Model.period == self._period,
                     self._Model.closed == int(closed)
                     )
            ).order_by(self._Model.time).all()
        return result

    def _save_records(self, records):
        new_records = [
            merge_dict(record, {'currency_pair': self._currency_pair,
                                'period': self._period,
                                'closed': True}
                       )
            for record in records
        ]
        self.create_multiple(new_records)
