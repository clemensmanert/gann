import logging

from gann.offer import offer_bitcoin_de

class TraderRunner:
    """ Runs a trader and prints trading activity."""
    def __init__(self, traders, depots, log):
        if len(traders) != len(depots):
            raise Exception("Trader and depot sizes do not machts")
        self.traders = traders
        self.depots = depots

        handler = logging.StreamHandler( log)
        handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
                             )

        logging.getLogger().addHandler(handler)

        logging.getLogger().setLevel(logging.INFO)

    def add_order(self, *args):
        """Progresses a given order"""
        for i in range(len(self.traders)):
            trader = self.traders[i]
            depot = self.depots[i]
            if trader.process_offer(offer_bitcoin_de(args[0])):
                depot.seek(0)
                depot.write(str({'money': trader.money,
                                 'depot': trader.depot}))
                # flush everythin else if previously written depot was larger.
                depot.truncate()

    def remove_order(self, *args):
        """Progress the removal of an order"""
        pass

    def refresh_express_option(self, *args):
        """Seems to occur sometimes at bitcoin.de
        TODO: Checkout how to handle it."""
        pass
