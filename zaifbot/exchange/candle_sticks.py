from zaifbot.db.dao.candle_sticks import CandleSticksDao
from zaifbot.exchange.api.http import BotChartApi
from zaifbot.exchange.period import Period
from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.utils import merge_dict, int_epoch_time


class CandleSticks:
    MAX_COUNT = 1500

    def __init__(self, currency_pair, period):
        self._currency_pair = CurrencyPair(currency_pair)
        self._period = Period(period)
        self._dao = CandleSticksDao(self._currency_pair, self._period)

    def request_data(self, count=100, to_epoch_time=None):
        count = min(count, self.MAX_COUNT)
        to_epoch_time = int_epoch_time(to_epoch_time)
        end_time_rounded = self._period.truncate_sec(to_epoch_time)
        start_time = self._period.calc_start(count, end_time_rounded)

        db_records = self._fetch_data_from_db(start_time=start_time, end_time=end_time_rounded)
        if len(db_records) >= count:
            return db_records

        api_records = self._fetch_data_from_web(start_time, end_time_rounded)
        return api_records

    def last_price(self,  timestamp):
        return self.request_data(count=1, to_epoch_time=timestamp)[0]['close']

    def _fetch_data_from_web(self, start_time, to_epoch_time):
        chart_api = BotChartApi()
        records = chart_api.history(self._currency_pair, self._period, start_time, to_epoch_time)
        self._save_records(records)
        return records

    def _save_records(self, records):
        new_records = [
            merge_dict(record, {'currency_pair': self._currency_pair.name,
                                'period': self._period.label,
                                'closed': True}
                       )
            for record in records
            ]
        self._dao.create_multiple(new_records)

    def _fetch_data_from_db(self, start_time, end_time):
        records = list(map(self._row2dict, self._dao.get_by_time_width(start_time, end_time, closed=True)))
        return records

    @staticmethod
    # todo: move to candle_sticks_dao
    def _row2dict(row):
        dict_row = row.__dict__
        dict_row.pop('_sa_instance_state', None)
        return dict_row
