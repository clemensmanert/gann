import unittest
import logging
import sys
import io

from datetime import datetime, timedelta

from gann.offer import Offer, OfferType
from gann.removal import Removal
from gann.trading_pair import TradingPair
from gann.serialization import (serialize_offer_to, serialize_removal_to,
                                deserialize_from)

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

class TestSerialisation(unittest.TestCase):

    def offer(self,
              offer_type,
              price,
              amount=2,
              min_amount=0.0,
              trading_pair=TradingPair.BTCEUR,
              date=datetime.now()):
        """Creates a new order for testing purposes"""
        self.offer_id += 1

        return Offer(
            order_id='#'+str(self.offer_id),
            amount=float(amount),
            min_amount=min_amount,
            price=price,
            offer_type=offer_type,
            trading_pair=trading_pair,
            date=date)

    def setUp(self):
        self.offer_id = 0

    def test_serialize_offer(self):
        """
        When serializing an offer expect to get an equal offer when
        deserialzing it.
        """
        expected = self.offer(offer_type=OfferType.SELL,
                              price=1000_00,
                              amount=2,
                              date=datetime.now() - timedelta(days=2))

        offer_buffer = io.BytesIO()
        serialize_offer_to(expected, offer_buffer)

        offer_buffer.seek(0,0)
        actuals = list(deserialize_from(offer_buffer))

        self.assertEqual(1, len(actuals))
        self.assertEqual(actuals[0], expected)

    def test_serialize_removal(self):
        """
        When serializing an removal expect to get an equal offer when
        deserialzing it.
        """
        expected = Removal("theId",
                           OfferType.BUY,
                           "reason",
                           0,
                           0.0,
                           date=datetime.now() - timedelta(days=2))

        removal_buffer = io.BytesIO()
        serialize_removal_to(expected, removal_buffer)

        removal_buffer.seek(0,0)
        actuals = list(deserialize_from(removal_buffer))

        self.assertEqual(1, len(actuals))
        self.assertEqual(actuals[0], expected)

    if __name__ == '__main__':
        unittest.main()
