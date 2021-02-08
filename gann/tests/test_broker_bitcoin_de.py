import unittest
from unittest import mock
from unittest.mock import Mock

import json
import logging
import sys
from typing import Dict

from gann.broker_bitcoin_de import BrokerBitcoinDe
from gann.offer import Offer, OfferType
from gann.trader_conditions import TradingPair

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)

class TradingLog:
    def   __init__(self):
        self.content = []

    def write(self, log_entry):
        # Ignore newlines
        if log_entry == '\n':
            return
        self.content.append(log_entry)

class MockResponse:
    """Mocks the response of a `requests.get(...)` call.
    Including status code and content."""
    def __init__(self, status_code:int = 200, content: Dict = None):
        self.status_code = status_code
        self.content = json.dumps(content)

class TestBrokerBitcoinDe(unittest.TestCase):

    def setUp(self):
        self.trading_log = TradingLog()
        self.target = BrokerBitcoinDe(trading_log=self.trading_log,
                                      api_key='xxx', secret='yyy', init_nonce=1)
    def test_post_headers(self):
        actual = self.target.post_headers('http://some.target/url',
                                          {'param1': 'value1',
                                           'param2': 'value2',
                                           'param3Int': 3})
        self.assertEqual(actual, {'X-API-KEY': 'xxx',
                                  'X-API-NONCE': '2',
                                  'X-API-SIGNATURE': '7bb5c80534678e3f4f7493163'
                                  '797ea102ba23c485396f92b74ec82487df45389'})

    def test_get_headers(self):
        actual = self.target.get_headers('http://some.target/url')
        self.assertEqual(actual, {'X-API-KEY': 'xxx',
                                  'X-API-NONCE': '2',
                                  'X-API-SIGNATURE': '69e89c9f154400e4c7fe76a8d'
                                  '82f991f33aefb42f324a5dd05a1c13d4eb7160c'})

    def test_nonce(self):
        """Expect the nonce's result to be greater after every call"""
        self.assertEqual('2', self.target.nonce())
        self.assertEqual('3', self.target.nonce())
        self.assertEqual('4', self.target.nonce())

    @mock.patch('requests.get', Mock(return_value=MockResponse(
        200, {'trade': {'amount_currency_to_trade_after_fee': 0.0009}})))
    def test_gained_coins_after_fees(self):

        actual = self.target.gained_coins_after_fees(
            Offer(
                order_id='some id',
                amount=1,
                min_amount=0.1,
                price=100_00,
                offer_type=OfferType.SELL,
                trading_pair=TradingPair.BTGEUR))

        self.assertEqual(actual, 0.0009)

    @mock.patch('requests.get', Mock(return_value=MockResponse(
        200, {'trade': {'volume_currency_to_pay_after_fee': 90_00}})))
    def test_gained_money_after_fees(self):
        actual = self.target.gained_money_after_fees(
            Offer(
                order_id='some id2',
                amount=1,
                min_amount=0.1,
                price=100_00,
                offer_type=OfferType.BUY,
                trading_pair=TradingPair.BTGEUR))

        self.assertEqual(actual, 90_00)

    @mock.patch('requests.post', Mock(return_value=MockResponse(
        422, {'errors': ['Order not possible'],
              'code': 51,
              'credits': 10})))
    def test_try_buy_fail(self):
        """Expect False if some buy request failed."""
        actual = self.target.try_buy(
            Offer(
                order_id='some id3',
                amount=1,
                min_amount=0.1,
                price=100_00,
                offer_type=OfferType.SELL,
                trading_pair=TradingPair.BTGEUR),
            amount=0.2)

        self.assertEqual(actual, False)
        self.assertEqual(0, len(self.trading_log.content))


    @mock.patch('requests.post', Mock(return_value=MockResponse(201)))
    @mock.patch('requests.get', Mock(return_value=MockResponse(
        200, {'trade': {'amount_currency_to_trade_after_fee': 0.19}})))
    def test_try_buy_success(self):
        """Expect the amount of bought coins if some buy request succeeded."""
        actual = self.target.try_buy(
            Offer(
                order_id='some id3',
                amount=1,
                min_amount=0.1,
                price=100_00,
                offer_type=OfferType.SELL,
                trading_pair=TradingPair.BTGEUR),
            amount=0.2)

        self.assertEqual(actual, 0.19)
        self.assertEqual(1, len(self.trading_log.content))

    @mock.patch('requests.post', Mock(return_value=MockResponse(
        422, {'errors': ['Order not possible'],
              'code': 51,
              'credits': 10})))
    def test_try_sell_fail(self):
        """Expect False if some sell request failed."""
        actual = self.target.try_sell(
            Offer(
                order_id='some id3',
                amount=1,
                min_amount=0.1,
                price=100_00,
                offer_type=OfferType.BUY,
                trading_pair=TradingPair.BTGEUR),
            amount=0.2)

        self.assertEqual(actual, False)
        self.assertEqual(0, len(self.trading_log.content))

    @mock.patch('requests.post', Mock(return_value=MockResponse(201)))
    @mock.patch('requests.get', Mock(return_value=MockResponse(
        200, {'trade': {'volume_currency_to_pay_after_fee': 99_90}})))
    def test_try_sell_success(self):
        """Expect the recevied money (after fees) if a selling was
        successfull."""
        self.assertEqual(0, len(self.trading_log.content))
        actual = self.target.try_sell(
            Offer(
                order_id='some id3',
                amount=1,
                min_amount=0.1,
                price=100_00,
                offer_type=OfferType.BUY,
                trading_pair=TradingPair.BTGEUR),
            amount=0.2)

        self.assertEqual(actual, 99_90)
        self.assertEqual(1, len(self.trading_log.content))

