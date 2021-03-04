import unittest
import logging
import sys

from gann.offer import Offer, OfferType
from gann.trader import Trader
from gann.trader_conditions import TraderConditions
from gann.trading_pair import TradingPair

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

INTITIAL_DEPOT = {5000_00: 0.01}

class TestBroker:
    """ In these tests we guess, that all trades work"""
    def __init__(self):
        pass

    def try_buy(self, offer, amount):
        return amount

    def try_sell(self, offer, amount):
        return offer.price * amount

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
        self.trader = Trader(depot=INTITIAL_DEPOT,
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

        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)

    def test_ignore_more_expensive_offers(self):
        """Expect to ignore a selling offer, if it is too exensive."""
        self.trader.process_offer(self.offer(amount=10,
                                             min_amount=1,
                                             price=999900,
                                             offer_type=OfferType.SELL))
        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)


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

    def test_sell_min_amount_too_high(self):
        """Expect to ignores a buying request, if delta is reached but min
        amount is too hight."""

        self.trader.process_offer(self.offer(
            amount=2.5,
            min_amount=2.5,
            price=6000_00,
            offer_type=OfferType.BUY))

        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)

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

    def test_too_little_profit(self):
        """Expect the trader not to buy anithing if it does not make any
        profit"""
        self.trader.process_offer(self.offer(OfferType.BUY, 5009_00, 0.02))

        self.assertEqual(self.trader.money, 1000_00)
        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)

    def test_enough_profit(self):
        """Expect the trader to sell, if it makes enoguht profit"""
        self.trader.process_offer(self.offer(OfferType.BUY, 6000_00, 0.01))

        self.assertEqual(self.trader.money, 1060_00)
        self.assertEqual(self.trader.depot, dict())

    def test_enough_profit_but_something_left(self):
        """Expect the trader have something left, if the offer asks for less
        than there is in depot."""
        self.trader.process_offer(self.offer(OfferType.BUY, 10000_00, 0.005))

        self.assertEqual(self.trader.money, 1050_00)
        self.assertEqual(self.trader.depot, {5000_00: 0.005})

    def test_enough_when_selling_two_positions(self):
        self.trader.depot[5010_00] = 0.01
        self.trader.money = 0

        self.trader.process_offer(self.offer(OfferType.BUY, 6000_00, 0.02,
                                             min_amount=0.02))

        self.assertEqual(self.trader.money, 120_00)
        self.assertEqual(self.trader.depot, dict())

    def test_sell_lower_position_when_highter_brings_no_profit(self):
        self.trader.depot[4300_00] = 0.01

        self.trader.process_offer(self.offer(OfferType.BUY, 5500_00, 0.01))
        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)

    def test_sell_partly_if_to_much_in_depot(self):
        self.trader.depot[5050_00] = 0.2

        self.trader.process_offer(self.offer(OfferType.BUY, 5600_00, 0.11))
        self.assertEqual(self.trader.depot, {5050_00: 0.1})

    def test_calculate_the_right_amount_to_sell(self):
        self.trader.depot[5000_00] = 1000

        self.trader.process_offer(self.offer(OfferType.BUY, 5500_00, 0.02))
        self.assertEqual(self.trader.depot, {5000_00: 999.98})

    def test_profit_as_persentage_sell(self):
        self.trader.conditions = TraderConditions(min_profit_price='10%')

        self.trader.process_offer(self.offer(OfferType.BUY, 5500_00, 0.01))
        self.assertEqual(self.trader.depot, {})
        self.assertEqual(self.trader.money, 1000_00 + 5500)

    def test_profit_as_persentage_hold(self):
        self.trader.conditions = TraderConditions(min_profit_price='10%')

        self.trader.process_offer(self.offer(OfferType.BUY, 5400_00, 0.01))
        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)
        self.assertEqual(self.trader.money, 1000_00)

    def test_do_not_buy_when_price_is_too_close_to_last_purchase(self):
        """Expect to ignore sellings where the price is too close to the
        last pruchase position."""

        self.trader.process_offer(self.offer(OfferType.SELL, 4999_00, 0.1, 0.0))
        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)
        self.assertEqual(self.trader.money, 1000_00)

    def test_do_not_buy_when_price_is_higher_than_last_purchase(self):
        """Expect to ignore sellings where the price is higher than the last
        position"""

        self.trader.process_offer(self.offer(OfferType.SELL, 5001_00, 0.1, 0.0))

        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)
        self.assertEqual(self.trader.money, 1000_00)

    def test_do_not_buy_when_there_is_not_enough_money(self):
        """Expect to ignore sellings we have too little money to buy."""
        self.trader.money = 1_00;

        self.trader.process_offer(self.offer(OfferType.SELL, 100_00, 1, 1))

        self.assertEqual(self.trader.depot, INTITIAL_DEPOT)
        self.assertEqual(self.trader.money, 1_00)

    def test_sell_only_profitalbe(self):
        """Expect to sell only the profitalbe positions,
        keep those who do not make profit"""
        self.trader.depot = {4024994: 0.002,
                             4018100: 0.002,
                             4000000: 0.002}

        self.trader.process_offer(self.offer(OfferType.BUY, 44000_00, 0.1, 0.0))

        self.assertEqual(self.trader.depot, {4024994: 0.002,
                                             4018100: 0.002})
        self.assertEqual(self.trader.money, 1000_00 + 88_00)

    if __name__ == '__main__':
        unittest.main()
