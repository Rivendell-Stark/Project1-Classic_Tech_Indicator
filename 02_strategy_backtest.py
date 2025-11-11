'''
实现策略并输出回测结果到 results 文件夹中
'''
from __future__ import (absolute_import, division, print_function, unicode_literals)  
import os.path
import sys

import datetime
import pandas as pd
import numpy as np
import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (
        ("maperiod", 15),
        ("printlog", False),
    )

    def log(self, txt, dt=None):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.maperiod)

        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("BUY EXECUTED, PRICE: %.2f, COST: %.2f, COMMISSION: %.2f" % 
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            elif order.issell():
                self.log("SELL EXECUTED, PRICE: %.2f, COST: %.2f, COMMISSION: %.2F" %
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % 
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log("Close, %.2f" % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log("BUY CREATE, %.2f" % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log("SELL CREATE, %.2f" % self.dataclose[0])
                self.order = self.sell()
    
if __name__ == "__main__":
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, "./data/orcl-1995-2014.txt")

    data = bt.feeds.YahooFinanceCSVData(
        dataname = datapath,
        fromdate = datetime.datetime(2000,1,1),
        todate = datetime.datetime(2000,12,31),
        reverse = False)
    
    cerebro.adddata(data)
    cerebro.broker.setcash(1000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)

    print("Srarting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()
    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()