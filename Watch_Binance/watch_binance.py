import os, requests, json
import sqlite3

from time import sleep, strftime, gmtime
from itertools import repeat

FLASK_PORT = int(os.getenv('FLASK_PORT'))
BINANCE_URL = os.getenv('BINANCE_URL')
API_DELAY = int(os.getenv('API_DELAY'))
SQLITE_FILE = os.getenv('SQLITE_FILE')
SLACK_URL = os.getenv('SLACK_URL')
USE_DATEFMT = os.getenv('USE_DATEFMT')

app = Flask(__name__)

class BinanceMonitor(object):
    def __init__(self, db):
        self.binance_url = BINANCE_URL
        self.delay = API_DELAY
        self.datefmt = USE_DATEFMT
        self.conn = sqlite3.connect(SQLITE_FILE)
        self.coins = []

    def run(self):
        while True:
            self.update()
            sleep(self.delay)

    def update(self):
        coins = self.scrape()
        diff = set(coins).difference(set(self.coins))
        if len(diff) > 1:
            sql = "DROP TABLE IF EXISTS coins"
            self.conn.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS coins " + \
                  "(coin TEXT PRIMARY_KEY)"
            self.conn.execute(sql)
        else:
            print("No new coins.")
        self.coins = coins

    def scrape(self):
        res = requests.get(self.binance_url)
        data = json.loads(res.text)
        coins = [x["assetCode"] for x in data]
        return coins

monitor = BinanceMonitor(SQLITE_FILE)
monitor.run()
