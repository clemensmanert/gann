from gann.offer import OfferType

def removal_bitcoin_de(removal_dict):
    """Factory method to create a removal using the data  provided by
    bitcoin.de's websocket.

    :param dict removal_dict: Containing the keys least oder_id,
    and offer_type. All values should be strings.
    """
    return Removal( removal_dict['order_id'],
                    OfferType(removal_dict['order_type']),
                    removal_dict.get('reason', '') )

class Removal:
    """Describes an offer, which has been removed"""
    def __init__(self, order_id, offer_type, reason):
        """Creates a removal.

        :param str order_id: The order's id.
        :param OfferType oder_type: Indicates whether the offer creater
        wants to sell or buy.
        :param str type todo: fix this.
        :param str reason why it was removed.
        """

        self.order_id = order_id
        self.offer_type = offer_type
        self.reason = reason

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

        return (self.order_id == other.order_id and
                self.offer_type == other.offer_type and
                self.reason == other.reason)
