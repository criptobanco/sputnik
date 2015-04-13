import sys

from twisted.python import log
from twisted.internet import reactor, ssl, task

from autobahn.twisted.websocket import connectWS

from sputnik import BotFactory
from random_trader import RandomBot
from market_maker import MarketMakerBot
import random
import string
import logging
import argparse

class LoadTester():
    def onMakeAccount(self, event):
        RandomBot.onMakeAccount(self, event)
        self.authenticate()

    def startAutomation(self):
        # Now make an account
        self.username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.makeAccount(self.username, self.password, "%s@m2.io" % self.username, "Test User %s" % self.username)

class MarketLoadTester(LoadTester, MarketMakerBot):
    pass

class RandomLoadTester(LoadTester, RandomBot):
    place_all_random = True
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test a Sputnik exchange under load')
    parser.add_argument('uri', help="the websockets URI for the exchange")
    parser.add_argument('-r', '--rate', type=float, help="pause in s between orders", default=1)
    parser.add_argument('-q', '--quantity', type=int, help="how many are we running", default=1)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--random', help="Run the random bot", action="store_true")
    group.add_argument('--market', help="Run the marketmaker bot", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s() %(lineno)d:\t %(message)s', level=logging.DEBUG)
    log.startLogging(sys.stdout)

    for i in range(args.quantity):
        factory = BotFactory(args.uri, debugWamp=False, rate=args.rate)
        if args.random:
            factory.protocol = RandomLoadTester
        elif args.market:
            factory.protocol = MarketLoadTester

        # null -> ....
        if factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None

        def failure():
            print "Unable to connect: %d" % i

        factory.connect(contextFactory, failure=failure)

    reactor.run()
