from zaifapi import ZaifPublicApi


def get_current_last_price(currency_pairs):
    api = ZaifPublicApi()#websocketに
    return api.last_price(currency_pairs)['last_price']
