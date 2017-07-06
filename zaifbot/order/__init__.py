class OrderMenu:
    from zaifbot.order.orders.limit_order import LimitOrder
    from zaifbot.order.orders.market_order import MarketOrder
    from zaifbot.order.orders.stop_order import StopOrder
    from zaifbot.order.orders.time_limit_cancel import TimeLimitCancel
    from zaifbot.order.orders.price_boundary_cancel import PriceBoundaryCancel

    def __init__(self):
        self.limit_order = self.LimitOrder
        self.market_order = self.MarketOrder
        self.stop_order = self.StopOrder
        self.time_limit_cancel = self.TimeLimitCancel
        self.price_boundary_cancel = self.PriceBoundaryCancel
