from zaifbot.modules.dao.bollinger_bands import BollingerBandsDao
from zaifbot.modules.moving_average import get_need_epoch_times
from zaifbot.models.bollinger_bands import BollingerBands
from zaifbot.moving_average import get_sma
import numpy as np


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
        sma_records = get_sma(self._currency_pair, self._period, self._count, end_time, self._length)
        for i in range(self._length, len(sma_records['return']['sma'])):
            if sma_records['return']['sma'][i]['time_stamp'] in target_epoch_times:
                nums = self._get_nums(sma_records['return']['sma'], i)
                standard_deviation = self._get_standard_deviation(nums)
                bollinger_bands_model_data.add(self._get_bollinger_bands_model_dataset
                                                   (sma_records['return']['sma'][i]['time_stamp'],
                                                    sma_records['return']['sma'][i]['close'],
                                                    standard_deviation,
                                                    sma_records['return']['sma'][i]['closed']))
        return self._bollinger_bands.create_data(bollinger_bands_model_data)

    def _get_target_epoch_times(self, start_time, end_time):
        bollinger_bands_record = self._bollinger_bands.get_records(end_time, start_time, True)
        return self._check_missing_records(bollinger_bands_record, start_time, end_time, self._period)

    @staticmethod
    def _check_missing_records(bollinger_bands_record, start_time, end_time, period):
        exist_epoch_times = set([x.time for x in bollinger_bands_record])
        target_epoch_times = set()
        for need_epoch_time in get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in exist_epoch_times:
                target_epoch_times.add(need_epoch_time)
        return target_epoch_times

    @staticmethod
    def _get_standard_deviation(nums):
        return np.sqrt(np.average(np.power(nums, 2)))

    def _get_nums(self, sma_records, i):
        nums = []
        for j in range(0, self._length):
            nums.append(sma_records[i - j]['close'] - sma_records[i]['moving_average'])
        return nums

    def _get_bollinger_bands_model_dataset(self, time, close, standard_deviation, closed):
        return BollingerBands(
            time=time,
            currency_pair=self._currency_pair,
            period=self._period,
            length=self._length,
            sd1p=close + standard_deviation,
            sd2p=close + (standard_deviation * 2),
            sd3p=close + (standard_deviation * 3),
            sd1n=close - standard_deviation,
            sd2n=close - (standard_deviation * 2),
            sd3n=close - (standard_deviation * 3),
            closed=closed)
