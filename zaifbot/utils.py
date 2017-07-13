from os import environ as env


# for dict
def merge_dict(base_dict, *dicts):
    for dic in dicts:
        base_dict.update(dic) or base_dict
    return base_dict


# # for trade_api
# def preset_keys(key, secret):
#     env['ZAIFBOT_KEY'] = key
#     env['ZAIFBOT_SECRET'] = secret
#
#
# def get_keys():
#     return env['ZAIFBOT_KEY'], env['ZAIFBOT_SECRET']


# def get_unique_trade_api(key=None, secret=None):
#     trade_api = None
#
#     def _create_trade_api():
#         nonlocal trade_api
#         if trade_api:
#             return trade_api
#         trade_api = BotTradeApi(key, secret)
#         return trade_api
#
#     trade_api = _create_trade_api()
#     return trade_api
#
#
# def set_trade_api(key, secret):
#     preset_keys(key, secret)
#     return get_unique_trade_api()
