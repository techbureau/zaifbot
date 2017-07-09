import time
from .wrapper import BotPublicApi
from zaifbot.dao import OhlcPricesDao
from zaifbot.utils import calc_start_from_count_and_end, truncate_time_at_period, merge_dict


class OhlcPrices:
    MAX_COUNT = 1500

    def __init__(self, currency_pair, period):
        self._currency_pair = currency_pair
        self._period = period
        self._dao = OhlcPricesDao(self._currency_pair, self._period)

    def fetch_data(self, count=100, to_epoch_time=None):
        count = min(count, self.MAX_COUNT)
        to_epoch_time = to_epoch_time or int(time.time())
        end_time_rounded = truncate_time_at_period(to_epoch_time, self._period)
        start_time = calc_start_from_count_and_end(count, end_time_rounded, self._period)

        db_records = self._fetch_data_from_db(start_time=start_time, end_time=end_time_rounded)
        if len(db_records) >= count:
            return db_records

        api_records = self._fetch_data_from_web(count, end_time_rounded)
        return api_records

    def _fetch_data_from_web(self, count, to_epoch_time):
        public_api = BotPublicApi()
        api_params = {'period': self._period, 'count': count, 'to_epoch_time': to_epoch_time}
        records = public_api.everything('ohlc_data', self._currency_pair, api_params)
        db_records = [merge_dict(record,
                                 {'currency_pair': self._currency_pair, 'period': self._period})
                      for record in records]

        self._dao.create_multiple(db_records)
        return records

    def _fetch_data_from_db(self, start_time, end_time):
        records = list(map(self._row2dict, self._dao.get_records(start_time, end_time, closed=False)))
        return records

    # todo: もっと汎用的な場所に移動させる
    @staticmethod
    def _row2dict(row):
        dict_row = row.__dict__
        dict_row.pop('_sa_instance_state', None)
        return dict_row
