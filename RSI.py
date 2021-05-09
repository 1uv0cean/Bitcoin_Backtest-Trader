import backtrader as bt
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

class RSI(bt.Strategy):
    params = (
        ("portfolio_frac",0.98),
    )

    def __init__(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash
        self.size = None
        self.order = None
        self.rsi = bt.indicators.RSI_SMA(self.data,self.data.close, period=21)

    def next(self):
        if self.order:
            return  # pending order execution. Waiting in orderbook
        
        print(
            f"DateTime {self.datas[0].datetime.datetime(0)}, "
            f"Price {self.data[0]:.2f}"
            f"Position {self.position.upopened}"
        )

        if not self.position:
            if self.rsi < 30:
                print("Starting buy order")
                self.size = (
                    self.broker.get_cash() / self.datas[0].close * self.p.portfolio_frac
                )
                self.order = self.buy(size=self.size)
        else:
            if self.rsi > 70:
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

cerebro.addstrategy(RSI)

cerebro.broker.addcommissioninfo(BitmexComissionInfo())

# Execute
results = cerebro.run()
st0 = results[0]

for alyzer in st0.analyzers:
                alyzer.print()
cerebro.plot(style = 'candlestick')
