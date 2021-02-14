from datetime import datetime

from enum import Enum, unique
from gann.trading_pair import TradingPair

@unique
class PaymentOption(Enum):
    NA = 0
    EXPRESS_ONLY = 1
    SEPA_ONLY = 2
    EXPRESS_SEPA = 3

@unique
class OfferType(Enum):
    """Specifies the type of an offer `sell` or `buy`."""
    BUY = "buy"
    SELL = "sell"

    def __str__(self):
        return str(self.value)

def offer_bitcoin_de(offer_dict):
    """Factory method to create an offer using the data  provided by
    bitcoin.de's websocket.
        :param dict offer_dict: Containing the keys least oder_id, amount,
    min_amount, price, oder_type. All values should be strings.
    """
    return Offer(
        offer_dict['order_id'],
        float(offer_dict['amount']),
        float(offer_dict['min_amount']),
        int(float(offer_dict['price']) * 100),
        OfferType(offer_dict['order_type']),
        TradingPair(offer_dict['trading_pair']),
        datetime.now(),
        list(PaymentOption)[int(offer_dict['payment_option'])]
    )

class Offer:
    """ An Offer to buy or sell coins. """
    def __init__(self, order_id, amount, min_amount, price, offer_type,
                 trading_pair, date=datetime.now(),
                 payment_option=PaymentOption.NA):
        """Creates an offer.
        :param str order_id: The order's id.
        :param float amount: The amount of coins which is offerd/asked for.
        :param float min_amount: The minimum amount of coins the vendor is
        willing to trade.
        :param int price: The offer's price as per coin in cents.
        :param OfferType oder_type: Indicates wether the offer creater  wants to
        sell or buy.
        :param TradingPair trading_pair: Specifies the type of coins this offer
        is about.
        :param datetime date: The point in time when the offer appeared.
        :param PaymentOption payment_option: The accepted option for this offer.
        """

        self.order_id = order_id
        self.amount = amount
        self.min_amount = min_amount
        self.price = price
        self.type = OfferType(offer_type)
        self.trading_pair = TradingPair(trading_pair)
        self.date = date
        self.payment_option = payment_option

    def __str__(self):
        return "#%s %4s %10.6f(%10.6f) for %8.2f € of %s" % (self.order_id,
                                                           self.type,
                                                        self.amount,
                                                        self.min_amount,
                                                        self.price/100.0,
                                                        self.trading_pair.value)
    def __eq__(self, other):
        if other is None:
            return False

        if self  is other:
            return  True

        if not isinstance(other, Offer):
            return False

        return (self.order_id == other.order_id and
                self.amount == other.amount and
                self.min_amount == other.min_amount and
                self.price == other.price and
                self.type == other.type and
                self.trading_pair == other.trading_pair and
                self.date == other.date and
                self.payment_option == other.payment_option)
