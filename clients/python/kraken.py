import treq
import json
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from twisted.python import log, failure
import string
import hmac
import hashlib
import time
from decimal import Decimal
from pprint import pprint
from datetime import datetime

class Kraken():
    def __init__(self, client_id=None, api_key=None, api_secret=None, endpoint="https://api.kraken.com"):
        self.client_id = client_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.endpoint = endpoint
        self.markets = {}
        self.ticker_map = {'BTC/USD': 'XXBTZUSD',
                           'BTC/LTC': 'XXBTXLTC'}


    @inlineCallbacks
    def handle_response(self, response):
        content = yield response.content()
        result = json.loads(content)
        returnValue(result['result'])

    def post(self, url, data={}):
        return treq.post(url, data=json.dumps(data)).addCallback(self.handle_response)

    def get(self, url, params={}):
        return treq.get(url, params=params).addCallback(self.handle_response)

    @inlineCallbacks
    def getMarkets(self):
        asset_pairs = yield self.get(self.endpoint + "/0/public/AssetPairs")
        assets = yield self.get(self.endpoint + "/0/public/Assets")
        assets.update(asset_pairs)
        # TODO: Process this into standard format
        self.markets = assets
        returnValue(assets)

    @inlineCallbacks
    def getOrderBook(self, ticker):
        if ticker in self.ticker_map:
            symbol = self.ticker_map[ticker]
            url = self.endpoint + "/0/public/Depth"
            params = {'pair': symbol}
            result = yield self.get(url, params=params)
            book = {'contract': ticker,
                    'bids': [{'price': Decimal(r[0]), 'quantity': Decimal(r[1])} for r in result[symbol]['bids']],
                    'asks': [{'price': Decimal(r[0]), 'quantity': Decimal(r[1])} for r in result[symbol]['asks']]
            }
            returnValue(book)
        else:
            raise NotImplementedError

if __name__ == "__main__":
    kraken = Kraken()
    d = kraken.getMarkets().addCallback(pprint)
    #d = kraken.getOrderBook('BTC/LTC').addCallback(pprint).addErrback(log.err)
    reactor.run()



