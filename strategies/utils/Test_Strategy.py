from __future__ import (absolute_import, division, print_function, unicode_literals) 

import backtrader as bt
import backtrader.indicator as btind
from .Base_Strategy import BaseStrategy

class TestStrategy(bt.Strategy):
    """一个简单的占位策略，用于验证数据加载和Cerebro运行。"""
    
    # 打印出每个数据源的名称和最新价格
    def next(self):
        for i, data in enumerate(self.datas):
            dt = self.datetime.date()
            if data.datetime[0] > 0:
                print(f'{dt} | {data._name} - Close: {data.close[0]:.2f}')

class BuyonceStrategy(BaseStrategy):
    """
    最简单的买入并持有策略，用作基准 (Benchmark)。
    它在第一根K线买入，一直持有到最后。
    """
    params = (
        ('target_pos', 0.95), 
        ('is_opt', False),     
    )

    def __init__(self):
        super().__init__()
        self.bought_once = False
        self.dataclose = self.datas[0].close

        self.order = None

    def next(self):
        if self.order:
            return

        if (not self.position)and (not self.bought_once):                
            if self.broker.getcash() > 0:                
                self.log(f'买入')
                self.order = self.order_target_percent(target=self.p.target_pos)
                self.bought_once = True
                
        if len(self) == (len(self.datas[0]) - 1): 
             self.close()
