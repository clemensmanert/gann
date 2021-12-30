from datetime import datetime

from gann.offer import OfferType

def removal_bitcoin_de(removal_dict):
    """Factory method to create a removal using the data  provided by
    bitcoin.de's websocket.

    :param dict removal_dict: Containing the keys least oder_id,
    and offer_type. All values should be strings.
    """
    return Removal( removal_dict['order_id']
                    , OfferType(removal_dict['order_type'])
                    , removal_dict.get('reason', '')
                    , int(removal_dict.get('price', 0) * 100)  # Euro vs cents
                    , removal_dict.get('amount', float('nan'))
                   )

class Removal:
    """Describes an offer, which has been removed"""
    def __init__(self, order_id, offer_type, reason, price=0, amount=float('nan'),
                 date=datetime.now()):
        """Creates a removal.

        :param str order_id: The order's id.
        :param OfferType oder_type: Indicates whether the offer creater
        wants to sell or buy.
        :param str type todo: fix this.
        :param str reason why it was removed.
        :param int price of the offer, can be null if it was not sold.
        :param float amount which was sol, can be null if it was not sold
        :param datetime date Point in time when the offer was removed.
        """

        self.order_id = order_id
        self.offer_type = offer_type
        self.reason = reason
        self.price = price
        self.amount = amount
        self.date = date

    def __str__(self):
        return "Removal %s %4s %s" % (self.order_id,
                                     self.offer_type,
                                     self.reason)

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, Removal):
            return False

        if self  is other:
            return  True

        return (self.order_id == other.order_id
                and self.offer_type == other.offer_type
                and self.reason == other.reason
                and self.date == other.date
                and self.price == other.price
                and self.amount == other.amount
                )
