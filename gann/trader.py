import logging
import sys

from gann.offer import OrderType
from gann.trader_conditions import TraderConditions

LOGGER = logging.getLogger()

class Trader:
    """A trader which remebers the assets it baught and will sell them only to a
    given amount of profit."""
    def __init__(self, broker, depot=None, money=0,
                 conditions=TraderConditions()):
        self.conditions = conditions
        self.last_purchase_price = 0.0
        self.money = money
        self.broker = broker

        self.lowest_price_selling = sys.maxsize
        self.highest_price_buying = 0

        if depot is None:
            self.depot = dict()
        else:
            # sorts dict by price, so that lower come first
            self.depot = dict(sorted(depot.items()))

        # Set cheapest price for last bought item
        if any(self.depot):
            self.last_purchase_price = list(self.depot)[0]

    def consider_buy(self, offer):
        """Takes an offer and buy to it if it matches the configured conditions
        taking the previously bought offers into account.
        ":param Offer offer: The offer to check.
        ":returns: `True` if the trader bought to it, `False` otherwise."""
        if offer.price < self.lowest_price_selling:
            self.lowest_price_selling = offer.price

        if offer.price * offer.min_amount > self.conditions.max_price():
            LOGGER.info("%s Don't buy because the min amount "
                        "is too hight.", offer)
            return

        if offer.price * offer.amount < self.conditions.min_price():
            LOGGER.info("%s Don't buy because the amount is "
                        "too small.", offer)
            return

        if any(self.depot):
            if offer.price > (self.last_purchase_price
                              - self.conditions.step_price):
                LOGGER.info("%s Don't buy because price is too close "
                            "to the last purchase. %.2f", offer,
                            self.last_purchase_price/100.0)
                return
        else:
            if offer.price > (self.highest_price_buying -
                              self.conditions.turnaround_price):
                LOGGER.info("%s Don't buy because the turnaround %.2f has not "
                            "been reached.",
                            offer,
                            (self.highest_price_buying
                             - self.conditions.turnaround_price) / 100.0)
                return

        amount = self.conditions.amount_price / offer.price

        if amount < offer.min_amount:
            amount = offer.min_amount

        if amount * offer.price > self.money:
            LOGGER.info("%s Don't buy because there is not enough money left.",
                        offer)
            return

        if not self.broker.try_buy(offer, amount):
            return

        self.money -= amount * offer.price
        self.last_purchase_price = offer.price
        LOGGER.info("%s Bought %f, money left: %i",
                    offer, amount, self.money)


        if offer.price in self.depot:
            self.depot[offer.price] += amount
        else:
            self.depot[offer.price] = amount

    def consider_sell(self, offer):
        """Takes an offer and sells to it if it matches the configured conditions
        taking the previously bought offers into account.
        ":param Offer offer: The offer to check.
        ":returns: `True` if the trader sold to it, `False` otherwise."""
        if offer.price > self.highest_price_buying:
            self.highest_price_buying = offer.price

        prices = sorted(
            filter(lambda p:
                   offer.price >= (p + self.conditions.min_profit_price),
                   list(self.depot)),
            reverse=True)

        amount = 0
        consumed = []
        left_in_depot_amount = 0
        while any(prices) and amount < offer.amount:
            if amount + self.depot[prices[0]] > offer.amount:
                left_in_depot_amount = offer.amount - amount
                left_in_depot_price = prices[0]
                amount = offer.amount
            else:
                amount += self.depot[prices[0]]
                consumed.append(prices[0])
                del prices[0]

        # Exit if we do not have enough in depot to make a profitalbe deal
        if offer.min_amount > amount:
            if amount == 0:
                LOGGER.info("%s Don't sell because we have nothing to make "
                            "profit.", offer)
            else:
                LOGGER.info("%s Don't sell because we only have %i "
                        "to make profit.", offer, amount)
            return

        if not self.broker.try_sell(offer, amount):
            return

        self.money += amount * offer.price

        for item in consumed:
            del self.depot[item]

        if left_in_depot_amount > 0:
            self.depot[left_in_depot_price] = left_in_depot_amount

    def process_offer(self, offer):
        if offer.trading_pair != self.conditions.trading_pair:
            return

        if offer.type == OrderType.BUY:
            # Someone wants to buy coins
            self.consider_sell(offer)
        elif offer.type == OrderType.SELL:
            # Someone wants to sell coins
            self.consider_buy(offer)

    def __str__(self):
        m = self.money/100
        return "%s, and %s" % (f"{m:,}", self.depot)

    def __repr__(self):
        return self.__str__()
