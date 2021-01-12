from enum import Enum, unique
from datetime import datetime

import struct
from gann.offer import OfferType, Offer, PaymentOption
from gann.trader_conditions import TradingPair
from gann.removal import Removal

@unique
class EVENT_TYPE (Enum):
    """Specifies if an offer is created or removed."""
    ADDED = 0
    REMOVED = 1

EVENT_TYPES_BY_INDEXES = dict(zip(
    list(range(len(list(EVENT_TYPE)))),
    list(EVENT_TYPE)
))

OFFER_TYPES_BY_INDEXES = dict(zip(
    list(range(len(list(OfferType)))),
    list(OfferType)
))

TRADING_PAIRS_BY_INDEXES = dict(zip(
    list(range(len(list(TradingPair)))),
    list(TradingPair)
))

INDEXES_BY_OFFER_TYPES = dict(zip(
    list(OfferType),
    list(range(len(list(OfferType))))
))

INDEXES_TRADING_PAIRS_INDEXES = dict(zip(
    list(TradingPair),
    list(range(len(list(TradingPair))))
))

PAYMENT_OPTIONS_BY_INDEXES = dict(zip(
    list(range(len(list(PaymentOption)))),
    list(PaymentOption)
))

EVENT_TYPE_STRUCT = struct.Struct('i')
OFFER_STRUCT = struct.Struct('6pdddiidi')
REMOVAL_STRUCT = struct.Struct('6pi20pd')

def deserialize_event(buffer):
    """Serializes the one event from the given buffer"""
    event_bin = EVENT_TYPE_STRUCT.unpack(buffer)
    return EVENT_TYPES_BY_INDEXES[event_bin[0]]

def deserialize_offer(buffer):
    """Deserialze a offer by reading binary data from a given buffer."""
    offer_bin = OFFER_STRUCT.unpack(buffer)
    return Offer(
        order_id=offer_bin[0].decode('utf-8'),
        amount=offer_bin[1],
        min_amount=offer_bin[2],
        price=offer_bin[3],
        offer_type=OFFER_TYPES_BY_INDEXES[offer_bin[4]],
        trading_pair=TRADING_PAIRS_BY_INDEXES[offer_bin[5]],
        date=datetime.fromtimestamp(offer_bin[6]),
        payment_option=PAYMENT_OPTIONS_BY_INDEXES[offer_bin[7]]
    )

def deserialize_removal(buffer):
    """Deserialze a removal by reading binary data from a given buffer."""
    removal_bin = REMOVAL_STRUCT.unpack(buffer)
    return Removal(
        order_id=removal_bin[0].decode(),
        offer_type=OFFER_TYPES_BY_INDEXES[removal_bin[1]],
        reason=removal_bin[2].decode(),
        date=datetime.fromtimestamp(removal_bin[3]))

def serialize_offer(offer):
    """Serialize a given offer into binary."""
    return EVENT_TYPE_STRUCT.pack(EVENT_TYPE.ADDED.value) + OFFER_STRUCT.pack(
        offer.order_id.encode('utf-8'),
        offer.amount,
        offer.min_amount,
        offer.price,
        INDEXES_BY_OFFER_TYPES[offer.type],
        INDEXES_TRADING_PAIRS_INDEXES[offer.trading_pair],
        offer.date.timestamp(),
        offer.payment_option.value)

def serialize_removal(removal):
    """Serialize a given removal into binary."""
    return (EVENT_TYPE_STRUCT.pack(EVENT_TYPE.REMOVED.value)
            + REMOVAL_STRUCT.pack(
                removal.order_id.encode(),
                INDEXES_BY_OFFER_TYPES[removal.offer_type],
                removal.reason.encode(),
                removal.date.timestamp()))


def serialize_offer_to(offer, buffer):
    """Serializes an offer to the given buffer"""
    buffer.write(serialize_offer(offer))

def serialize_removal_to(removal, buffer):
    """Serializes a removal to the given buffer."""
    buffer.write(serialize_removal(removal))

def deserialize_from(buffer):
    """Reads and deserialzes offers and removals from a given buffer."""
    while next_offer_event := buffer.read(EVENT_TYPE_STRUCT.size):
        if deserialize_event(next_offer_event) == EVENT_TYPE.ADDED:
            yield deserialize_offer(buffer.read(OFFER_STRUCT.size))
        else:
            yield deserialize_removal(buffer.read(REMOVAL_STRUCT.size))
