from zaifbot.db.dao.candle_sticks import CandleSticksDao
from zaifbot.exchange.api.http import BotPublicApi
from zaifbot.exchange.period import Period
from zaifbot.utils import merge_dict, int_time


class CandleSticks:
    MAX_COUNT = 1500

    def __init__(self, currency_pair, period):
        self._currency_pair = currency_pair
        self._period = Period(period)
        self._dao = CandleSticksDao(self._currency_pair, self._period)

    def request_data(self, count=100, to_epoch_time=None):
        count = min(count, self.MAX_COUNT)
        to_epoch_time = to_epoch_time or int_time()
        end_time_rounded = self._period.truncate_sec(to_epoch_time)
        start_time = self._period.calc_start(count, end_time_rounded)

        db_records = self._fetch_data_from_db(start_time=start_time, end_time=end_time_rounded)
        if len(db_records) >= count:
            return db_records

        api_records = self._fetch_data_from_web(count, end_time_rounded)
        return api_records

    def last_price(self,  timestamp):
        return self.request_data(count=1, to_epoch_time=timestamp)[0]['close']

    def _fetch_data_from_web(self, count, to_epoch_time):
        public_api = BotPublicApi()
        api_params = {'period': self._period, 'count': count, 'to_epoch_time': to_epoch_time}
        records = public_api.everything('ohlc_data', self._currency_pair, api_params)
        db_records = [merge_dict(record,
                                 {'currency_pair': str(self._currency_pair), 'period': str(self._period)})
                      for record in records]
        self._dao.create_multiple(db_records)
        return records

    def _fetch_data_from_db(self, start_time, end_time):
        records = list(map(self._row2dict, self._dao.get_by_time_width(start_time, end_time, closed=False)))
        return records

    @staticmethod
    def _row2dict(row):
        dict_row = row.__dict__
        dict_row.pop('_sa_instance_state', None)
        return dict_row
