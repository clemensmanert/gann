import hashlib
import hmac
import json
import logging
import time
from typing import Dict
from urllib.parse import urlencode
import requests

from gann.offer import Offer, OfferType

LOGGER = logging.getLogger()
class BrokerBitcoinDe:
    """A Broker to interact with the *bitcoin.de* market place."""
    API_URL = "https://api.bitcoin.de/v4/"
    def __init__(self, trading_log, api_key: str, secret: str,
                 init_nonce: int = int(time.time())):
        self.trading_log = trading_log
        self.api_key = api_key
        self.secret = secret
        self.last_nonce = init_nonce

    def nonce(self):
        self.last_nonce += 1
        return str(self.last_nonce)

    def post_headers(self, uri: str, post_params: Dict):
        """Creates the post headers for an uri and post parameters

        :param:"""
        nonce = self.nonce();
        sorted_post_params = dict(sorted(post_params.items()))
        post_params_str = urlencode(sorted_post_params)
        post_params_md5 = hashlib.md5(post_params_str.encode("utf-8"))
        message = '#'.join(['POST',
                            uri,
                            self.api_key,
                            nonce,
                            post_params_md5.digest().hex()])

        signature = hmac.digest(self.secret.encode("utf-8"),
                                msg=message.encode("utf-8"),
                                digest='sha256').hex()

        return {"X-API-KEY": self.api_key,
                "X-API-NONCE": nonce,
                "X-API-SIGNATURE": signature}

    def get_headers(self, uri: str):
        nonce = self.nonce()

        # No Post params -> empty string
        post_params_md5 = hashlib.md5(str().encode("utf-8"))
        message = '#'.join(['GET',
                            uri,
                            self.api_key,
                            nonce,
                            post_params_md5.digest().hex()])

        signature = hmac.digest(self.secret.encode("utf-8"),
                                msg=message.encode("utf-8"),
                                digest='sha256').hex()

        return {"X-API-KEY": self.api_key,
                "X-API-NONCE": nonce,
                "X-API-SIGNATURE": signature}

    def gained_coins_after_fees(self, offer: Offer):
        """ Returns the amount of coins recefied for a succesful `SELL`-order.
        :param offer: The targeted offer.
        """
        if offer.type != OfferType.SELL:
            raise Exception("Can not calculate coins for an offer which is not "
                            "of type `SELL` %s" % offer)
        url = (self.API_URL + "/"
               + offer.trading_pair.value
               + "/trades/"
               + offer.order_id
               )

        result = requests.get(url, headers=self.get_headers(url))

        if result.status_code != 200:
            LOGGER.error("Failed to get last trades coins amount due to %i: %s",
                         result.status_code,  result.content.decode("utf-8"))
            return False
        coins = float(json.loads(result.content)['trade']
                      ['amount_currency_to_trade_after_fee'])
        if coins  < 0 or coins > offer.amount:
            LOGGER.error("Failed to determine gained coins. '%f' seems "
                         "not to be a correct value.", coins)
            return False
        return coins


    def gained_money_after_fees(self, offer: Offer):
        """ Returns the amount of mony recefied for a succesful `BUY`-order.
        :param offer: The targeted offer.
        """

        if offer.type != OfferType.BUY:
            raise Exception("Can not calculate money for an offer which is not "
                            "of type `BUY` %s" % offer)
        url = (self.API_URL + "/"
               + offer.trading_pair.value + "/trades/"
               + offer.order_id)

        result = requests.get(url, headers=self.get_headers(url))

        if result.status_code != 200:
            LOGGER.error("Failed to get last trades moiny after fees amount due"
                         " to %i: %s", result.status_code,
                         result.content.decode("utf-8"))
            return False
        money = float(json.loads(result.content)['trade']
                      ['volume_currency_to_pay_after_fee'])

        if money < 0 or money > offer.price * offer.amount:
            LOGGER.error("Failed to determine correct gained money %f seems "
                         "not to  be a correct", result)
            return False
        return int(money * 100)

    def try_buy(self, offer: Offer, amount: float):
        url = (self.API_URL + offer.trading_pair.value
               + "/trades/" + offer.order_id)
        data = {'type': "buy",
                'payment_option': offer.payment_option.value,
                'amount_currency_to_trade': amount}
        result = requests.post(url,
                               headers=self.post_headers(url, data),
                               data=data)

        if result.status_code == 201:
            print("Successfully bought %f %s of %s" % (
                amount, offer.trading_pair.value, offer),
                  file=self.trading_log)
            return self.gained_coins_after_fees(offer)

        LOGGER.error("Failed to buy %f as %s (%i) %s",
                     amount, offer, result.status_code, result.content)
        return False

    def try_sell(self, offer: Offer, amount: float):
        url = (self.API_URL + offer.trading_pair.value
               + "/trades/" + offer.order_id)
        data = {'type': "sell",
                'payment_option': 1,
                'amount_currency_to_trade': amount}
        result = requests.post(url, data, headers=self.post_headers(url, data))

        if result.status_code == 201:
            print("Successfully sold %f %s of %s" % (
                amount, offer.trading_pair.value, offer),
                  file=self.trading_log)
            return self.gained_money_after_fees(offer)

        LOGGER.error("Failed to sell %f as %s (%i) %s",
                     amount, offer,result.status_code, result.content)
        return False
