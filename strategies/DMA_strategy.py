'''
策略: 单股票双均线择时策略

开仓信号: 金叉 + 无持仓

平仓信号: 死叉 + 有持仓

止损信号: 无
'''
from __future__ import (absolute_import, division, print_function, unicode_literals)  

import os
import logging
from typing import TextIO

import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import backtrader.indicators as btind

from .utils import BaseStrategy

class DMAStrategy(BaseStrategy):
    # --- A. 策略参数设置 ---
    params = (
        ("fast", 20),
        ("slow", 60),
        ("loss_stop", 0.05),
        ('target_pos', 0.95)
        )
    
    # --- B.1 策略初始化 ---
    def __init__(self):
        super().__init__()
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open

        self.fast_ma = btind.MovingAverageSimple(self.datas[0].close, period=self.p.fast, plot=True)
        self.slow_ma = btind.MovingAverageSimple(self.datas[0].close, period=self.p.slow, plot=True)
        self.cross_over = btind.CrossOver(self.fast_ma, self.slow_ma)

    # --- B.2 策略周期执行 ---
    def next(self):
        
        buy_sig = self.cross_over[0] > 0
        sell_sig = self.cross_over[0] < 0
        risk_sig = self.datas[0].low[0] <= (self.buyprice * (1.0 - self.p.loss_stop))

        if self.order:
            return

        if not self.position:
            if buy_sig:
                self.log("买入信号产生: 金叉")
                self.order = self.order_target_percent(target=self.p.target_pos)
        else:
            if sell_sig:
                self.log("卖出信号产生: 死叉")
                self.order = self.close()
            elif risk_sig:
                self.log(f"止损信号产生: 损失超过{self.p.loss_stop: .2%}")