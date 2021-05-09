import matplotlib.pyplot as plt
from datetime import datetime
from os import path
import backtrader as bt
import pandas as pd
date_from = "2021-01-01"
date_to = "2021-04-30"
output_folder = "data/bitmex"
dates = pd.date_range(date_from, date_to).astype(str).str.replace("-", "")
dataset_filename = path.join(output_folder, f"XBT_USD_{date_from}_{date_to}.csv")

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

class SmaCross(bt.Strategy): # bt.Strategy를 상속한 class로 생성해야 함.

    params = dict(
        pfast=5, # period for the fast moving average
        pslow=30, # period for the slow moving average
        portfolio_frac= 0.98,
    )

    def __init__(self):
        self.val_start = self.broker.get_cash() 
        self.size = None
        self.order = None
        sma1 = bt.ind.SMA(self.data,period=self.p.pfast) # fast moving average
        sma2 = bt.ind.SMA(self.data,period=self.p.pslow) # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2) # crossover signal

    def next(self):
        if self.order:
            return

        print(
            f"DateTime {self.datas[0].datetime.datetime(0)}, "
            f"Price {self.data[0]:.2f}"
            f"Position {self.position.upopened}"
        )

        if not self.position: # not in the market
            if self.crossover > 0: # if fast crosses slow to the upside
                print("Starting buy order")
                self.size = (
                    self.broker.get_cash() / self.datas[0].close * self.p.portfolio_frac
                )
                self.order = self.buy(size=self.size)

        else:
            if self.crossover < 0: # in the market & cross to the downside
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
cerebro = bt.Cerebro() # create a "Cerebro" engine instance

cerebro.broker.setcash(1000) # 초기 자본 설정

data = bt.feeds.GenericCSVData(
    dataname=dataset_filename,
    dtformat="%Y-%m-%d %H:%M",
    timeframe=bt.TimeFrame.Ticks,
)

cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)

cerebro.addstrategy(SmaCross) # 자신만의 매매 전략 추가

cerebro.broker.addcommissioninfo(BitmexComissionInfo())

results = cerebro.run()
st0 = results[0]

for alyzer in st0.analyzers:
                alyzer.print()

plt.rcParams["figure.figsize"] = (60,30)
cerebro.plot(style = 'candlestick')
