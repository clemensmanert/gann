import logging
import sys

class TraderRunner:
    """ Runs a trader and prints trading activity."""
    def __init__(self, traders=None, depots=None, log=sys.stdout):
        self.traders = traders if traders is not None else list()
        self.depots = depots if depots is not None else list()

        handler = logging.StreamHandler(log)
        handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
                             )

        logging.getLogger().addHandler(handler)

        logging.getLogger().setLevel(logging.INFO)

    def add_order(self, offer):
        """Progresses a given order"""

        if len(self.traders) != len(self.depots):
            raise Exception("Trader and depot sizes do not machts")

        for i in range(len(self.traders)):
            trader = self.traders[i]
            depot = self.depots[i]
            if trader.process_offer(offer):
                depot.seek(0)
                depot.write(str({'money': trader.money,
                                 'depot': trader.depot}))
                # flush everythin else if previously written depot was larger.
                depot.truncate()
                depot.flush()
                # skip other traders, since this offers gone now
                return

    def remove_order(self, *args):
        """Progress the removal of an order"""

    def refresh_express_option(self, *args):
        """Seems to occur sometimes at bitcoin.de
        TODO: Checkout how to handle it."""
