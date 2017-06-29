class OrderMenu:
    from .limit_order import LimitOrder
    from .market_order import MarketOrder
    from .stop_order import StopOrder
    from .time_limit_cancel import TimeLimitCancel
    from .price_boundary_cancel import PriceBoundaryCancel

    def __init__(self):
        self.limit_order = self.LimitOrder
        self.market_order = self.MarketOrder
        self.stop_order = self.StopOrder
        self.time_limit_cancel = self.TimeLimitCancel
        self.price_boundary_cancel = self.PriceBoundaryCancel
