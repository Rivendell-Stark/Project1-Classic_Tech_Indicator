'''
策略: 沪深300双均线择时, 短sma5-长sma20, 过滤条件: 超过 5% 长均线 + 收盘价低于长均线

'''
from __future__ import (absolute_import, division, print_function, unicode_literals)  
import os.path
import sys

import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds

class TestStrategy(bt.Strategy):
    params = (
        ("ma_short", 5),
        ("ma_long", 20),
        ("filter", 0.005),
        ("printlog", True),
    )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))
    
    def __init__(self):
        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma_short = btind.MovingAverageSimple(self.datas[0], period=self.params.ma_short)
        self.sma_long = btind.MovingAverageSimple(self.datas[0], period=self.params.ma_long)

        self.golden_cross = btind.CrossOver(self.sma_short, self.sma_long)
        self.death_cross = btind.CrossOver(self.sma_long, self.sma_short)



        btind.ExponentialMovingAverage(self.datas[0], period=25)
        btind.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        btind.StochasticSlow(self.datas[0])
        btind.MACDHisto(self.datas[0])
        rsi = btind.RSI(self.datas[0])
        btind.SmoothedMovingAverage(rsi, period=10)
        btind.ATR(self.datas[0], plot=False)


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
            if (self.golden_cross[0] == 1) and ((self.sma_short[0]-self.sma_long[0])/self.sma_long[0] >= self.params.filter) and (self.datas[0].close[0] > self.sma_long[0]):
            # if self.golden_cross[0] == 1:
                self.log("BUY CREATE, %.2f" % self.dataclose[0])
                self.order = self.buy()
        else:
            if (self.death_cross[0] == 1) and ((self.sma_long[0]-self.sma_short[0])/self.sma_long[0] >= self.params.filter) and (self.datas[0].close[0] < self.sma_long[0]):
            # if self.death_cross[0] == 1:
                self.log("SELL CREATE, %.2f" % self.dataclose[0])
                self.order = self.sell()
    
if __name__ == "__main__":

    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, "./data/hs300-22-25.csv")

    data = btfeeds.GenericCSVData(
        dataname = datapath,
        fromdate = datetime.datetime(2022,1,1),
        todate = datetime.datetime(2025,12,31),
        dtformat=(r'%Y/%m/%d'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
        )
    
    cerebro.adddata(data)
    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.001, margin=1.0, mult=1.0)

    print("Srarting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    results = cerebro.run()
    strat = results[0]
    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    core_metrics = {
        '策略名称': '5-20双均线择时',
        '标的': '沪深300',
        '回测时间': '2022-01-01 ~ 2025-11-10',
        '初始资金': 1000000,
        '最终净值': round(cerebro.broker.getvalue(), 2),
        '总收益率(%)': round(strat.analyzers.returns.get_analysis()['rtot'] * 100, 2),
        '年化收益率': round(strat.analyzers.returns.get_analysis()['rnorm100'], 2),
        '夏普比率': round(strat.analyzers.sharpe.get_analysis()['sharperatio'], 2),
        '最大回撤(%)': round(strat.analyzers.dd.get_analysis()['max']['drawdown'], 2),
        '总交易次数': strat.analyzers.trade_analyzer.get_analysis()['total']['total'],
        # '胜率(%)': round(strat.analyzers.trade_analyzer.get_analysis()['won']['total'] / strat.analyzers.trade_analyzer.get_analysis()['total']['total'] * 100, 2) if strat.analyzers.trade_analyzer.get_analysis()['total']['total'] > 0 else 0,
        # '盈亏比': round(strat.analyzers.trade_analyzer.get_analysis()['gross']['profit'] / abs(strat.analyzers.trade_analyzer.get_analysis()['gross']['loss']), 2) if strat.analyzers.trade_analyzer.get_analysis()['gross']['loss'] != 0 else 0
    }
    core_metrics_df = pd.DataFrame(core_metrics, index=core_metrics.keys())

    # trade_list = []
    # for trade in strat._trades:
    #     trade_dict  = {
    #         # '交易ID': trade.ref,
    #         '开仓时间': trade.open_datetime().strftime('%Y-%m-%d'),
    #         '开仓价格': round(trade.price, 2),
    #         '平仓时间': trade.close_datetime().strftime('%Y-%m-%d') if trade.closed else '未平仓',
    #         '平仓价格': round(trade.close_price, 2) if trade.closed else None,
    #         '持仓天数': (trade.close_datetime() - trade.open_datetime()).days if trade.closed else None,
    #         '盈亏金额': round(trade.pnl, 2),
    #         '手续费': round(trade.commission, 2),
    #         '净盈亏': round(trade.pnl - trade.commission, 2)
    #     }
    #     trade_list.append(trade_dict)
    # trade_df = pd.DataFrame(trade_list)

    # net_value_list = []
    # for i, data in enumerate(strat.data):
    #     net_value_dict = {
    #         '日期': data.datetime.date().strftime('%Y-%m-%d'),
    #         '账户净值': round(cerebro.broker.getvalue(), 2),
    #         '累计收益率(%)': round((cerebro.broker.getvalue() - 100000)/100000 * 100, 2),
    #         '标的收盘价': round(data.close[0], 2)
    #     }
    #     net_value_list.append(net_value_dict)
    # net_value_df = pd.DataFrame(net_value_list)

    with pd.ExcelWriter('双均线策略_回测结果.xlsx', engine='openpyxl') as writer:
        core_metrics_df.to_excel(writer, sheet_name='核心指标', index=False)
        # trade_df.to_excel(writer, sheet_name='交易明细', index=False)
        # net_value_df.to_excel(writer, sheet_name='净值曲线', index=False)

    # cerebro.plot()