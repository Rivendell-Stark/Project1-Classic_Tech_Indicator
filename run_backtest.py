'''
策略: 沪深300双均线择时, 短sma5-长sma20, 过滤条件: 超过 5% 长均线 + 收盘价低于长均线

'''
from __future__ import (absolute_import, division, print_function, unicode_literals)  
import os.path
import sys
from data.data_loader import load_stock_data
import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import quantstats as qt

class TestStrategy(bt.Strategy):
    params = (
        ("ma_short", 5),
        ("ma_long", 20),
        ("adx_period", 14),
        ("adx_threshold", 25),
        ("stop_loss_pct", 0.05),
        ("printlog", False),
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

        # buy_sig = self.cross_up[0] and (self.adx[0] > self.p.adx_threshold)
        # sell_sig = self.cross_down[0] or (self.buyprice and (self.datas[0].close[0] < self.buyprice * (1 - self.p.stop_loss_pct))) 

        buy_sig = self.cross_up[0]
        sell_sig = self.cross_down[0]

        if self.order:
            return

        if not self.position:
            if buy_sig:
                self.log("BUY CREATE, %.2f" % self.datas[0].close[0])
                self.order = self.order_target_percent(target=0.95)
                # self.order = self.buy()
        else:
            if sell_sig:
                self.log("SELL CREATE, %.2f" % self.datas[0].close[0])
                self.order = self.order_target_percent(target=0)
                # self.order = self.sell()

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


if __name__ == "__main__":

    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    
    data_pool = ['300519']
    start_date = datetime.datetime(2016,1,1)
    end_date = datetime.datetime(2025,12,31)

    stock_data_dict = load_stock_data(data_pool, start_date, end_date)

    for code, df in stock_data_dict.items():
        data = btfeeds.PandasData(dataname=df, name=code)
        cerebro.adddata(data)
    
    cerebro.broker.setcash(1000000.0)
    # cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.broker.set_checksubmit(True)
    cerebro.broker.set_fundmode(False)
    cerebro.broker.set_filler(None)

    print("Srarting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    results = cerebro.run()
    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    strategy_results = results[0]

    total_return = strategy_results.analyzers.returns.get_analysis()['rtot']
    annual_return = strategy_results.analyzers.returns.get_analysis()['rnorm100']
    sharpe_ratio = strategy_results.analyzers.sharpe.get_analysis()['sharperatio']
    max_drawdown = strategy_results.analyzers.drawdown.get_analysis()['max']['drawdown']

    trade_analysis = strategy_results.analyzers.trade_analyzer.get_analysis()
    trade_data = trade_analysis.get("total", {})
    total_trades = trade_data.get("closed", 0)
    winning_trades = trade_analysis.get('won', {}).get('total', 0)
    losing_trades = trade_analysis.get('lost', {}).get('total', 0)
    win_rate = (winning_trades / total_trades) * 100 if total_trades else 0

    print("================================== 策略性能分析 ==================================")
    print(f"基准 (沪深300指数双均线策略)")
    print(f"总交易次数: {total_trades}")
    print(f"胜率 (Winning Rate): {win_rate:.2f}%")
    print("----------------------------------- 收益指标 -----------------------------------")
    print(f"累计收益率 (Total Return): {total_return * 100:.2f}%")
    print(f"年化收益率 (Annualized Return): {annual_return:.2f}%")
    print(f"夏普比率 (Sharpe Ratio): {sharpe_ratio:.4f}")
    print("----------------------------------- 风险指标 -----------------------------------")
    print(f"最大回撤 (Max Drawdown): {max_drawdown:.2f}%")
    print("================================================================================")

    cerebro.plot()