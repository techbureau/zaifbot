from zaifapi import ZaifPublicApi
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
from zaifbot.modules.dao.moving_average import TradeLogsDao


class TradeLogsManager:
    def __init__(self, currency_pair, period):
        self._currency_pair = currency_pair
        self._period = period
        self._trade_logs = TradeLogsDao(self._currency_pair, self._period)

    def setup(self, start_epoch_time, end_epoch_time):
        target_epoch_times = self._get_target_epoch_times(start_epoch_time, end_epoch_time)
        if len(target_epoch_times) == 0:
            return
        api_records = self._get_ohlc_data_from_server(end_epoch_time)
        target_trade_logs_record = list(filter(lambda x: x['time'] in target_epoch_times, api_records))
        #ここにtarget_trade_logs_recordをSQLAlcemyのTradeLogsの配列に変換する処理を入れて、下の関数に渡す
        self._trade_logs.create_data(target_trade_logs_record)

    def _get_target_epoch_times(self, start_epoch_time, end_epoch_time):
        trade_logs_record = self._trade_logs.get_record(end_epoch_time, start_epoch_time)
        return self._check_missing_records(trade_logs_record, start_epoch_time, end_epoch_time, self._period)

    def _check_missing_records(self, trade_logs_record, start_time, end_time, period):
        to_epoch_times = set([x.time for x in trade_logs_record])
        target_epoch_times = set()
        for need_epoch_time in self._get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in to_epoch_times:
                target_epoch_times.add(need_epoch_time)
        return target_epoch_times

    @classmethod
    def _get_need_epoch_times(cls, start_time, end_time, period):
        while True:
            yield start_time
            start_time += PERIOD_SECS[period]
            if start_time >= end_time:
                yield end_time
                break

    def _get_ohlc_data_from_server(self, end_epoch_time):
        public_api = ZaifPublicApi()
        api_params = {'period': self._period, 'count': LIMIT_COUNT, 'to_epoch_time': end_time}
        return public_api.everything('ohlc_data', self._currency_pair, api_params)
