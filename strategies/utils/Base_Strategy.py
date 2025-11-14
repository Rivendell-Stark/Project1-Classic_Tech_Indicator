from __future__ import (absolute_import, division, print_function, unicode_literals)  

import os
import logging
from typing import TextIO

import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import backtrader.indicators as btind

class BaseStrategy(bt.Strategy):
    params = (
        ('log_dir', None),
        ('sys_logger', None),
    )

    def __init__(self):

        # --- 交易日志初始化 ---
        log_path = os.path.join(self.p.log_dir, "strategy_details.log") if self.p.log_dir else None
        self.strategy_log_file: TextIO = None

        strategy_name = self.__class__.__name__

        params_dict = self.p._getkwargs()
        excluded_keys = ['log_dir', 'sys_logger']
        params_str = ", ".join([
            f"{k}={v}" for k, v in params_dict.items()
            if k not in excluded_keys and not k.startswith("_")
        ])
        
        if log_path:
            try:
                self.strategy_log_file = open(log_path, "a", encoding='utf-8')
                self.log(f"策略({strategy_name})初始化完成。数据源: {self.data._name}")
                self.log(f"策略参数: {params_str}")
            except Exception as e:
                if self.p.sys_logger:
                    self.p.sys_logger.error(f"FATAL ERROR: 策略 ({strategy_name}) 无法打开详情日志文件: {log_path}。错误信息: {e}")
                print(f"FATAL ERROR: 策略 ({strategy_name}) 无法打开日志文件: {log_path}. Error: {e}")

        self.buyprice = 0.0
        self.buycomm = 0.0
        self.order = None
        self.bar_executed = len(self)

    def log(self, txt, dt=None, level=logging.INFO):
        """核心交易逻辑日志记录，写入到独立文件"""
        dt = dt or self.datas[0].datetime.date(0)
        log_line = f"[{self.data._name}] {dt.isoformat()} | {txt}\n"
        if self.strategy_log_file:
            self.strategy_log_file.write(log_line)
            self.strategy_log_file.flush()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("买入订单执行, 价格: %.2f, 成本: %.2f, 佣金费用: %.2f" % 
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            elif order.issell():
                self.log("卖出订单执行, 价格: %.2f, 成本: %.2f, 佣金费用: %.2f" %
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单失败: {}'.format(order.getstatusname()), level=logging.WARNING)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易关闭 - 记录盈亏: 毛利润 {:.2f}, 净利润 {:.2f}'.format(
                  trade.pnl, trade.pnlcomm))
        
    def stop(self):
        """回测结束后，关闭文件句柄"""
        if self.strategy_log_file:
            self.log(f"BaseStrategy finished for {self.data._name}.")
            self.strategy_log_file.close()