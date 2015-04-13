from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from twisted.python import log
from pprint import pprint
import treq
from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

class Yahoo():
    def __init__(self, **kwargs):
        self.yahoo_uri = "http://finance.yahoo.com/"
        self.oanda_uri = "http://www.oanda.com/currency/"

    @inlineCallbacks
    def getOrderBook(self, ticker):
        payout, denominated = ticker.split('/')
        url =  self.yahoo_uri + "q"
        params = {'s': "%s%s=X" % (payout, denominated)}
        response = yield treq.get(url, params=params)
        content = yield response.content()
        soup = BeautifulSoup(content)
        bid = Decimal(soup.find(id="yfs_b00_%s%s=x" % (payout.lower(), denominated.lower())).text.replace(',', ''))
        ask = Decimal(soup.find(id="yfs_a00_%s%s=x" % (payout.lower(), denominated.lower())).text.replace(',', ''))
        book = {'contract': ticker,
                'bids': [{'price': bid, 'quantity': 0}],
                'asks': [{'price': ask, 'quantity': 0}]}
        returnValue(book)

    @inlineCallbacks
    def getOHLCVHistory(self, ticker, period="day", start_datetime=None, end_datetime=None):
        payout, denominated = ticker.split('/')

        url = self.oanda_uri + "historical-rates/update"
        params = {'date_fmt': 'us',
                  'start_date': start_datetime.strftime('%Y-%m-%d'),
                  'end_date': end_datetime.strftime('%Y-%m-%d'),
                  'period': "daily",
                  'quote_currency': payout,
                  'base_currency_0': denominated,
                  'rate': 0,
                  'view': 'table',
                  'display': 'absolute',
                  'price': 'bid',
                  'data_range': 'd90'}
        headers = {'X-Requested-With': 'XMLHttpRequest',
                   'X-Prototype-Version': '1.7',
                   'Referer': 'http://www.oanda.com/currency/historical-rates/'}
        try:
            response = yield treq.get(url, params=params, headers=headers)
        except Exception as e:
            pass
        content = yield response.content()
        parsed = json.loads(content)
        data = parsed['widget'][0]['data']
        ohlcv_history = {}

        for row in data:
            date = datetime.fromtimestamp(row[0]/1e3)
            price = float(row[1])
            epoch = datetime.utcfromtimestamp(0)
            open_timestamp = int((date - epoch).total_seconds() * 1e6)
            tomorrow_date = date + timedelta(days=1)
            close_timestamp = int((tomorrow_date - epoch).total_seconds() * 1e6) - 1

            ohlcv = {
                'contract': ticker,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': 0,
                'vwap': price,
                'open_timestamp': open_timestamp,
                'close_timestamp': close_timestamp,
                'period': period
            }
            ohlcv_history[open_timestamp] = ohlcv

        returnValue(ohlcv_history)




if __name__ == "__main__":
    yahoo = Yahoo()
    #d = yahoo.getOrderBook('USD/MXN')
    #d.addCallback(pprint).addErrback(log.err)
    now = datetime.utcnow()
    d2 = yahoo.getOHLCVHistory('USD/HUF', start_datetime=now-timedelta(days=30), end_datetime=now)
    d2.addCallback(pprint).addErrback(log.err)

    reactor.run()
