from dataclasses import dataclass, field

from gann.trading_pair import TradingPair
from gann.offer import Offer

@dataclass(frozen=False)
class TraderConditions:
    """Conditions how the trader should respond to offers and sane defaults.

        :param int amount_price: Specifies how much the trader should spend for
        each asset at once
        :param int amount_pri ce_tolerance: Specifies how much the price is
        allowed to for each asset.
        :param int min_profit_price: Specifies how much profit each selling must
        generate.
        :param int step_price: Specifies how much the price has to decline,
                               unitl the trader should buy the next asse.t
        :param int turnaround_price: Specifies how much the price has to
                                     decline, until the trader should start
        buying again.
        :param int decimals: Tell the trader to round desired couins to some
                             decimal places, to produce not too obscure numbers.
        :param TradingPair trading_pair: Specifies the tradint pair, the trader
        should use.
        """
    amount_price: int = 100_00
    amount_price_tolerance: int = 20_00
    min_profit_str: str = '1000'
    step_price: int = 10_00
    turnaround_price: int = 10_00
    decimals: int = 4
    trading_pair: TradingPair = TradingPair.BTCEUR
    min_profit: int = field(init=False)
    percentage: bool = field(init=False)

    def __post_init__(self):
        if (isinstance(self.min_profit_str, str)
            and self.min_profit_str.endswith('%')):
            self.min_profit = int(self.min_profit_str[:-1])
            self.percentage = True
        else:
            self.min_profit = int(self.min_profit_str)
            self.percentage = False

    def max_price(self):
        return self.amount_price + self.amount_price_tolerance

    def min_price(self):
        return self.amount_price - self.amount_price_tolerance

    def enough(self,
               amount: float,
               offer: Offer,
               initial_spent: int) -> bool:

        if self.percentage:
            return (offer.price * amount
                 >= ( initial_spent *(1 + self.min_profit / 100)))

        return  (amount * offer.price >= (
            initial_spent/self.amount_price * self.min_profit +
            initial_spent))
