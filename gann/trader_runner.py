import json
import sys

class TraderRunner:
    """ Runs traders and persists their depots."""
    def __init__(self, traders=None, depots=None):
        self.traders = traders if traders is not None else list()
        self.depots = depots if depots is not None else list()

    def add_order(self, offer):
        """Progresses a given order"""

        if len(self.traders) != len(self.depots):
            raise Exception("Trader and depot sizes do not match.")

        for i in range(len(self.traders)):
            trader = self.traders[i]
            depot = self.depots[i]
            if trader.process_offer(offer):
                depot.seek(0)
                depot.write(json.dumps(
                    {"money": trader.money,
                     "depot": trader.depot}))
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
