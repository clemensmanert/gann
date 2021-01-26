import hashlib
import hmac
import logging

from urllib.parse import urlencode
import time
import requests

LOGGER = logging.getLogger()
class BrokerBitcoinDe:
    """A Broker to interact with the *bitcoin.de* market place."""
    API_URL = "https://api.bitcoin.de/v4/"
    def __init__(self, trading_log, api_key, secret):
        self.trading_log = trading_log
        self._nonce = 0
        self.api_key = api_key
        self.secret = secret

    def nonce(self):
        self._nonce += 1
        return self._nonce

    def post_headers(self, uri, post_params):
        nonce = str(int(time.time()))
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
                                digest=hashlib.sha256).hex()

        return {"X-API-KEY": self.api_key,
                "X-API-NONCE": nonce,
                "X-API-SIGNATURE": signature}

    def try_buy(self, offer, amount):
        url = (self.API_URL + offer.trading_pair.value
               + "/trades/" + offer.order_id)
        data = {'type': "buy",
                'payment_option': offer.payment_option,
                'amount_currency_to_trade': amount}
        result = requests.post(url,
                               headers=self.post_headers(url, data))

        if result.status_code == 201:
            print("Buying %s succeeded", self.trading_log)
            return True

        LOGGER.error("Failed to buy %f as %s (%i) %s",
                     amount, offer, result.status_code, result.content)
        return False

    def try_sell(self, offer, amount):
        url = (self.API_URL + offer.trading_pair.value
               + "/trades/" + offer.order_id)
        data = {'type': "sell",
                'payment_option': 1,
                'amount_currency_to_trade': amount}
        result = requests.post(url, data, headers=self.post_headers(url, data))

        if result.status_code == 201:
            print("Selling %s succeeded", self.trading_log)
            return True

        LOGGER.error("Failed to sell %f as %s (%i) %s",
                     amount, offer,result.status_code, result.content)
        return False
