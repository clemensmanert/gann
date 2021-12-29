from enum import Enum, unique

@unique
class TradingPair(Enum):
    BTCEUR = 'btceur'
    ETHEUR = 'etheur'
    BSVEUR = 'bsveur'
    BCHEUR = 'bcheur'
    BTGEUR = 'btgeur'
    LTCEUR = 'ltceur'
    XRPEUR = 'xrpeur'
    DOGEEUR = 'dogeeur'
    UNKNOWN = 'unknown'
