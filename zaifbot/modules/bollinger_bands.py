from zaifbot.modules.dao.bollinger_bands import BollingerBandsDao
from zaifbot.modules.moving_average import get_need_epoch_times
from zaifbot.models.bollinger_bands import BollingerBands
from zaifbot.moving_average import get_sma
import pandas as pd


class BollingerBandsSetUp:
    def __init__(self, currency_pair, period, count, length):
        self._currency_pair = currency_pair
        self._period = period
        self._count = count
        self._length = length
        self._bollinger_bands = BollingerBandsDao(self._currency_pair, self._period, self._length)

    def execute(self, start_time, end_time):
        bollinger_bands_model_data = set()
        target_epoch_times = self._get_target_epoch_times(start_time, end_time)
        if len(target_epoch_times) == 0:
            return True
        sma_records = get_sma(self._currency_pair, self._period,
                              self._count + self._length, end_time, self._length)
        if sma_records['success'] == 0:
            return False
        sma_records_df = pd.DataFrame(sma_records['return']['sma'])
        for i in range(self._length, len(sma_records_df.index)):
            if sma_records_df.loc[i]['time_stamp'] in target_epoch_times:
                standard_deviation = \
                    sma_records_df.loc[i - self._length:i]['close'].std(axis=0, ddof=0)
                bollinger_bands_model_data.add(self._get_bollinger_bands_model_dataset
                                               (sma_records['return']['sma'][i]['time_stamp'],
                                                sma_records['return']['sma'][i]['moving_average'],
                                                standard_deviation,
                                                sma_records['return']['sma'][i]['closed']))
        return self._bollinger_bands.create_data(bollinger_bands_model_data)

    def _get_target_epoch_times(self, start_time, end_time):
        bollinger_bands_record = \
            set([x.time for x in self._bollinger_bands.get_records(end_time, start_time, True)])
        return self._check_missing_records(bollinger_bands_record, start_time,
                                           end_time, self._period)

    @staticmethod
    def _check_missing_records(exist_epoch_times, start_time, end_time, period):
        need_epoch_times = \
            set([x for x in get_need_epoch_times(start_time, end_time, period)])
        return need_epoch_times.difference(exist_epoch_times)

    def _get_bollinger_bands_model_dataset(self, time, sma, standard_deviation, closed):
        return BollingerBands(
            time=time,
            currency_pair=self._currency_pair,
            period=self._period,
            length=self._length,
            sd1p=sma + standard_deviation,
            sd2p=sma + (standard_deviation * 2),
            sd3p=sma + (standard_deviation * 3),
            sd1n=sma - standard_deviation,
            sd2n=sma - (standard_deviation * 2),
            sd3n=sma - (standard_deviation * 3),
            closed=closed)
