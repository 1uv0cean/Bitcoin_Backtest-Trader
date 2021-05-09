
import pandas as pd
date_from = "2021-01-01"
date_to = "2021-04-30"
dates = pd.date_range(date_from, date_to).astype(str).str.replace("-", "")

import requests
from os import path
BASE_URL = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/%s"

def download_trade_file(filename, output_folder):
    print(f"Downloading {filename} file")
    url = BASE_URL % filename
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Cannot download the {filename} file. Status code: {resp.status_code}")
        return
    with open(path.join(output_folder, filename), "wb") as f:
        f.write(resp.content)
    print(f"{filename} downloaded")

output_folder = "data/bitmex"
for date in dates:
    filename = date + ".csv.gz"
    #download_trade_file(filename, output_folder)

import glob
filepaths = glob.glob(path.join(output_folder, "*.csv.gz"))
filepaths = sorted(filepaths)
filepaths
################
'''
df_list = []
for filepath in filepaths:
    print(f"Reading {filepath}")
    df_ = pd.read_csv(filepath)
    df_ = df_[df_.symbol == "XBTUSD"]
    print(f"Read {df_.shape[0]} rows")
    df_list.append(df_)
df = pd.concat(df_list)
df_list = None
df_ = None
df.loc[:, "Datetime"] = pd.to_datetime(df.timestamp.str.replace("D", "T"))
df.drop("timestamp", axis=1, inplace=True)
df = df.groupby(pd.Grouper(key="Datetime", freq="1Min")).agg(
    {"price": ["first", "max", "min", "last"], "foreignNotional": "sum"}
)
df.columns = ["Open", "High", "Low", "Close", "Volume"]
df.loc[:, "OpenInterest"] = 0.0 # required by backtrader
df = df[df.Close.notnull()]
df.reset_index(inplace=True)
df.to_csv(f'XBT_USD_{date_from}_{date_to}.csv')
'''
################
dataset_filename = path.join(output_folder, f"XBT_USD_{date_from}_{date_to}.csv")
import backtrader as bt
class BitmexComissionInfo(bt.CommissionInfo):
    params = (
        ("commission", 0.00075),
        ("mult", 1.0),
        ("margin", None),
        ("commtype", None),
        ("stocklike", False),
        ("percabs", False),
        ("interest", 0.0),
        ("interest_long", False),
        ("leverage", 1.0),
        ("automargin", False),
    )
    def getsize(self, price, cash):
        """Returns fractional size for cash operation @price"""
        return self.p.leverage * (cash / price)

class MACD(bt.Strategy):
    params = (
        ("macd1", 12),
        ("macd2", 26),
        ("macdsig", 9),
        # Percentage of portfolio for a trade. Something is left for the fees
        # otherwise orders would be rejected
        ("portfolio_frac", 0.98),
    )

    def __init__(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash
        self.size = None
        self.order = None

        self.macd = bt.ind.MACD(
            self.data,
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig,
        )
        # Cross of macd and macd signal
        self.mcross = bt.ind.CrossOver(self.macd.macd, self.macd.signal)
    
    def next(self):
        if self.order:
            return  # pending order execution. Waiting in orderbook

        print(
            f"DateTime {self.datas[0].datetime.datetime(0)}, "
            f"Price {self.data[0]:.2f}, Mcross {self.mcross[0]}, "
            f"Position {self.position.upopened}"
        )

        if not self.position:  # not in the market
            if self.mcross[0] > 0.0:
                print("Starting buy order")
                self.size = (
                    self.broker.get_cash() / self.datas[0].close * self.p.portfolio_frac
                )
                self.order = self.buy(size=self.size)
        else:  # in the market
            if self.mcross[0] < 0.0:
                print("Starting sell order")
                self.order = self.sell(size=self.size)
    def notify_order(self, order):
        """Execute when buy or sell is triggered
        Notify if order was accepted or rejected
        """
        if order.alive():
            print("Order is alive")
            # submitted, accepted, partial, created
            # Returns if the order is in a status in which it can still be executed
            return

        order_side = "Buy" if order.isbuy() else "Sell"
        if order.status == order.Completed:
            print(
                (
                    f"{order_side} Order Completed -  Size: {order.executed.size} "
                    f"@Price: {order.executed.price} "
                    f"Value: {order.executed.value:.2f} "
                    f"Comm: {order.executed.comm:.6f} "
                )
            )
        elif order.status in {order.Canceled, order.Margin, order.Rejected}:
            print(f"{order_side} Order Canceled/Margin/Rejected")
        self.order = None  # indicate no order pending
        
    def notify_trade(self, trade):
        """Execute after each trade
        Calcuate Gross and Net Profit/loss"""
        if not trade.isclosed:
            return
        print(f"Operational profit, Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}")

    def stop(self):
        """ Calculate the actual returns """
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        val_end = self.broker.get_value()
        print(
            f"ROI: {100.0 * self.roi:.2f}%%, Start cash {self.val_start:.2f}, "
            f"End cash: {val_end:.2f}"
        )

cerebro = bt.Cerebro()

cerebro.broker.set_cash(1000)

data = bt.feeds.GenericCSVData(
    dataname=dataset_filename,
    dtformat="%Y-%m-%d %H:%M",
    timeframe=bt.TimeFrame.Ticks,
)

cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)

cerebro.addstrategy(MACD)

cerebro.broker.addcommissioninfo(BitmexComissionInfo())

# Execute
results = cerebro.run()
st0 = results[0]

for alyzer in st0.analyzers:
                alyzer.print()
cerebro.plot(style = 'candlestick')
