from enum import Enum, unique
from gann.trader_conditions import TradingPair

@unique
class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

class Offer:
    """ An Offer to buy or sell coins. """
    def __init__(self, order_id, amount, min_amount, price, order_type,
                 trading_pair):
        """Creates an offer.
        :param str order_id: The order's id.
        :param float amount: The amount of coins which is offerd/asked for.
        :param float min_amount: The minimum amount of coins the vendor is
        willing to trade.
        :param int price: The offer's price as per coin in cents.
        :param OrderType oder_type: Indicates wether the offer creater  wants to
        sell or buy.
        :param TradingPair trading_pair: Specifies the type of coins this offer
        is about.
        """

        self.order_id = order_id
        self.amount = amount
        self.min_amount = min_amount
        self.price = price
        self.type = OrderType(order_type)
        self.trading_pair = TradingPair(trading_pair)

    def __str__(self):
        return "#%s %f for %f € of %s" % (self.order_id,
                                          self.amount,
                                          self.price,
                                          self.trading_pair)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.order_id == other.order_id and
                self.amount == other.amount and
                self.min_amount == other.min_amount and
                self.price == other.price and
                self.type == other.type and
                self.trading_pair == other.trading_pair)
