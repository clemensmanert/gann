import unittest
import logging
import sys

from gann.offer import Offer, OfferType
from gann.trader import Trader
from gann.trader_conditions import TraderConditions, TradingPair

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

class TestBroker:
    def __init__(self):
        pass

    """ In these tests we guess, that all trades work"""
    def try_buy(self, offer, amount):
        return True

    def try_sell(self, offer, amount):
        return True

class TestTrader(unittest.TestCase):

    def offer(self,
              offer_type,
              price,
              amount=2,
              min_amount=0.0,
              trading_pair=TradingPair.BTCEUR):
        """Creates a new order for testing purposes"""
        self.offer_id += 1

        return Offer(
            order_id=self.offer_id,
            amount=amount,
            min_amount=min_amount,
            price=price,
            offer_type=offer_type,
            trading_pair=trading_pair)

    def setUp(self):
        self.offer_id = 0
        self.trader = Trader(depot={5000_00:
                                    0.01},
                             money=1000_00,
                             conditions=TraderConditions(),
                             broker=TestBroker())

    def test_ignore_other_currencies(self):
        """Expect to ignore offers which propose the wrong currency."""
        # Wrong currency
        self.trader.process_offer(
            self.offer(amount=10,
                       min_amount=0.01,
                       price=123_00,
                       offer_type=OfferType.SELL,
                       trading_pair=TradingPair.BTGEUR))

        self.assertEqual(self.trader.depot, {5000_00: 0.01})

    def test_ignore_more_expensive_offers(self):
        """Expect to ignore a selling offer, if it is too exensive."""
        self.trader.process_offer(self.offer(amount=10,
                                             min_amount=1,
                                             price=999900,
                                             offer_type=OfferType.SELL))
        self.assertEqual(self.trader.depot, {5000_00: 0.01})


    def test_irgnore_too_hight_min_amounts(self):
        """Expect to ignore a selling offer, if the min amount is too high."""
        too_high_min_amount = self.offer(amount=100,
                                         min_amount=10,
                                         price=400000,
                                         offer_type=OfferType.SELL)
        self.trader.process_offer(too_high_min_amount)

        self.assertEqual(len(self.trader.depot), 1)

    def test_buy_fitting_offer(self):
        """ Expect trader to buy a offer which price is below
        last_bought_price - `step_size` """
        self.trader.process_offer(self.offer(amount=10,
                                             price=4500_00,
                                             offer_type=OfferType.SELL))
        self.assertEqual(self.trader.depot, {5000_00: 0.01,
                                             4500_00: 0.0222})

    def test_buy_another_fitting_offer(self):
        """ Expect trader to buy two offers in a row if each one's
        price is less than last_bought_price -  `step_price` """
        self.trader.process_offer(self.offer(amount=10,
                                             price=4990_00,
                                             offer_type=OfferType.SELL))

        self.assertEqual(self.trader.depot, {5000_00: 0.01,
                                             4990_00: 0.02})

        self.trader.process_offer(self.offer(amount=10,
                                             price=4980_00,
                                             offer_type=OfferType.SELL))

        self.assertEqual(self.trader.depot, {5000_00: 0.01,
                                             4990_00: 0.02,
                                             4980_00: 0.0201})

    def test_buy_if_min_amount_gt_amount_price_allows(self):
        """ Expects to buy the min amount, if it is still in range but the
        minamount is greater than the amount price."""

        self.trader.process_offer(self.offer(amount=10,
                                             min_amount=0.026,
                                             price=4000_00,
                                             offer_type=OfferType.SELL))

        self.assertEqual(self.trader.depot, {5000_00: 0.01,
                                             4000_00: 0.026})


    def test_ignore_too_little_amouint(self):
        """Expoect to ignore a offer where the min amount is too low."""
        self.trader.process_offer(
            self.offer(
                amount=0.5,
                min_amount=0.01,
                price=10,
                offer_type=OfferType.SELL))
        self.assertEqual(len(self.trader.depot), 1)

    def test_expect_not_to_sell_if_price_is_outisde_delta(self):
        """Expect not to sell, if delta is not reached."""

        self.trader.depot[3000_00] = 0.01

        self.trader.process_offer(self.offer(
            amount=2.5,
            min_amount=0.01,
            price=0.01,
            offer_type=OfferType.SELL))

        self.assertEqual(len(self.trader.depot), 2)

    def test_expect_to_sell_if_price_is_outisde_delta(self):
        """Expect to meet a sell offer, if delta is reached."""

        self.trader.depot[4990_00] = 0.02
        self.trader.last_purchase_price = 4990_00

        self.trader.process_offer(self.offer(
            amount=2.5,
            min_amount=0.01,
            price=5000_00,
            offer_type=OfferType.BUY))

        self.assertEqual(self.trader.depot, {5000_00: 0.01})

    def test_sell_min_amount_too_high(self):
        """Expect to ignores a buying request, if delta is reached but min
        amount is too hight."""

        self.trader.process_offer(self.offer(
            amount=2.5,
            min_amount=2.5,
            price=6000_00,
            offer_type=OfferType.BUY))

        self.assertEqual(self.trader.depot, {5000_00: 0.01})

    def test_start_buying_on_turnaround(self):
        """Expects to start buying, when starting with an empty depot and a
        turnaround is reached."""
        self.trader = Trader(broker=TestBroker(), money=1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 7000_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.BUY, 6050_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        # Local maximum
        self.trader.process_offer(self.offer(OfferType.SELL, 7100_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.BUY, 6150_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        # Declining prices
        self.trader.process_offer(self.offer(OfferType.SELL, 6000_00, 1))
        # Expect a position for last offer
        self.assertEqual(self.trader.depot, {6000_00:  0.0167})
        self.assertEqual(self.trader.money, 899_80)


    def test_not_tobuy_when_there_is_no_turnaround(self):
        """Expects not to buy as long as no turnaround is reached."""
        self.trader = Trader(broker=TestBroker(), money=1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 7000_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 7010_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 8010_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.BUY, 6080_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 6090_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 8000_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 9000_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.BUY, 5080_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.BUY, 6000_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

        self.trader.process_offer(self.offer(OfferType.SELL, 8000_00, 1))
        self.assertEqual(self.trader.depot, dict())
        self.assertEqual(self.trader.money, 1000_00)

    if __name__ == '__main__':
        unittest.main()
