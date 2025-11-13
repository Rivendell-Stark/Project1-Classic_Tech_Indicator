'''
策略: 沪深300双均线择时, 短sma5-长sma20, 过滤条件: 超过 5% 长均线 + 收盘价低于长均线

'''
from __future__ import (absolute_import, division, print_function, unicode_literals)  

import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import backtrader.indicators as btind

class DMA_Strategy(bt.Strategy):
    params = (
        ("ma_short", 5),
        ("ma_long", 20),
        ("adx_period", 14),
        ("adx_threshold", 25),
        ("stop_loss_pct", 0.05),
        ("printlog", True),
        )
    
    def __init__(self):
        self.sma_s = btind.MovingAverageSimple(self.datas[0].close, period=self.p.ma_short)
        self.sma_l = btind.MovingAverageSimple(self.datas[0].close, period=self.p.ma_long)
        
        self.adx = btind.AverageDirectionalMovementIndex(self.data, period=self.p.adx_period)

        self.cross_up = btind.CrossUp(self.sma_s, self.sma_l)
        self.cross_down = btind.CrossDown(self.sma_s, self.sma_l)

        self.buyprice = None
        self.buycomm = None
        self.order = None

    def next(self):
        self.log("Close, %.2f" % self.datas[0].close[0])

        buy_sig = self.cross_up[0] and (self.adx[0] > self.p.adx_threshold)
        sell_sig = self.cross_down[0] or (self.buyprice and (self.datas[0].close[0] < self.buyprice * (1 - self.p.stop_loss_pct))) 


        if self.order:
            return

        if not self.position:
            if buy_sig:
                self.log("BUY CREATE, %.2f" % self.datas[0].close[0])
                # self.order = self.order_target_percent(target=0.05)
                self.order = self.buy()
        else:
            if sell_sig:
                self.log("SELL CREATE, %.2f" % self.datas[0].close[0])
                # self.order = self.order_target_percent(target=0)
                self.order = self.sell()

    def log(self, txt, dt=None, doprint=False):
        if self.p.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

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
                
                self.buyprice = None
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % 
                 (trade.pnl, trade.pnlcomm))
