from enum import Enum, unique

@unique
class TradingPair(Enum):
    BTCEUR = 'btceur'
    ETHEUR = 'etheur'
    BSVEUR = 'bsveur'
    BCHEUR = 'bcheur'
    BTGEUR = 'btgeur'
    LTCEUR = 'ltceur'
    UNKNOWN = 'unknown'

class TraderConditions:
    """ The conditions on which the trader should decide when to buy/sell. """

    def __init__(self,
                 amount_price=100_00,
                 amount_price_tolerance=20_00,
                 min_profit_price=10_00,
                 step_price=10_00,
                 turnaround_price=10_00,
                 trading_pair=TradingPair.BTCEUR):
        """Conditions how the trader should respond to offers and sane defaults.

        :param int amount_price: Specifies how much the trader should spend for
        each asset at once
        :param int amount_pri ce_tolerance: Specifies how much the price is
        allowed to for each asset.
        :param int min_profit_price: Specifies how much profit each selling must
        generate.
        :param int step_price: Specifies how much the price has to decline,
                               unitl the trader should buy the next asset.
        :param int turnaround_price: Specifies how much the price has to
                                     decline, until the trader should start
        buying again.
        :param TradingPair trading_pair: Specifies the tradint pair, the trader
        should use.
        """

        self.amount_price = amount_price
        self.amount_price_tolerance = amount_price_tolerance
        self.min_profit_price = min_profit_price
        self.step_price = step_price
        self.turnaround_price = turnaround_price
        self.trading_pair = trading_pair

    def max_price(self):
        return self.amount_price + self.amount_price_tolerance

    def min_price(self):
        return self.amount_price - self.amount_price_tolerance
