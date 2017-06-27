import time

from wrapper import BotPublicApi
from zaifbot.bot_common.bot_const import LIMIT_COUNT
from zaifbot.dao.ohlc_prices import OhlcPricesDao
from zaifbot.utils import calc_start_from_count_and_end, truncate_time_at_period


class OhlcPrices:
    def __init__(self, currency_pair, period):
        self._currency_pair = currency_pair
        self._period = period
        self._dao = OhlcPricesDao(self._currency_pair, self._period)

    def fetch_data(self, count=LIMIT_COUNT, to_epoch_time=None):
        count = min(count, LIMIT_COUNT)
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
        self._dao.create_data(records)
        return records

    def _fetch_data_from_db(self, start_time, end_time):
        records = list(map(self._row2dict, self._dao.get_records(end_time, start_time, closed=False)))
        return records

    # todo: もっと汎用的な場所に移動させる
    @staticmethod
    def _row2dict(row):
        dict_row = row.__dict__
        dict_row.pop('_sa_instance_state', None)
        return dict_row
