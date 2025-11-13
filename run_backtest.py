'''
策略: 沪深300双均线择时, 短sma5-长sma20, 过滤条件: 超过 5% 长均线 + 收盘价低于长均线

'''
from __future__ import (absolute_import, division, print_function, unicode_literals)  

import os
import time
import logging

import datetime
import pandas as pd
import numpy as np
import quantstats as qt
import pyfolio as pf

import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanal
import backtrader.indicators as btind

from data import load_stock_data
from strategies import DummyStrategy
from utils import setup_output_run

# --- 1. 配置 ---
STRATEGY_NAME = 'DummyStrategy'
DATA_POOL = ['000001','300059','600519']
START_DATE = datetime.datetime(2016,1,1).strftime(r'%Y-%m-%d')
END_DATE = datetime.datetime(2025,12,31).strftime(r'%Y-%m-%d')

def run_backtest():
    
    # --- A. 初始化输出和日志 ---
    output_dir, logger = setup_output_run(STRATEGY_NAME, START_DATE, END_DATE)
    logger.info(f"回测开始: {STRATEGY_NAME}")
    logger.info(f"回测结果保存路径: {output_dir}")
    
    # --- B. 加载数据 ---
    stock_data_dict = load_stock_data(DATA_POOL, START_DATE, END_DATE)

    if not stock_data_dict:
        print("未读取到有效数据...")
        return
    
    # --- C. 配置 Cerebro ---
    cerebro = bt.Cerebro()

    # --- C.1 初始资金与费用设置 ---
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)
    # cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # --- C.2 添加数据源 ---
    for code, df in stock_data_dict.items():
        data = btfeeds.PandasData(dataname=df, name=code)
        cerebro.adddata(data)

    # --- C.3 添加策略 ---
    cerebro.addstrategy(DummyStrategy)

    # --- C.4 配置分析器 ---
    cerebro.addanalyzer(btanal.Returns, _name='returns')
    cerebro.addanalyzer(btanal.TimeDrawDown, _name='drawdown')
    cerebro.addanalyzer(btanal.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanal.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(btanal.PyFolio, _name='pyfolio')

    # --- C.5 配置交易记录 ---
    trades_path = os.path.join(output_dir, 'trades_records.csv')
    cerebro.addwriter(
        bt.WriterFile,
        csv=True,
        out=trades_path
    )

    # --- D. 运行回测 ---
    print("Srarting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    results = cerebro.run()    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # --- E. 回测结果分析 ---
    if not results:
        logger.error("回测失败，无结果")
        return

    strat = results[0]

    analysis_returns = strat.analyzers.getbyname("returns").get_analysis()
    analysis_drawdown = strat.analyzers.getbyname("drawdown").get_analysis()
    analysis_sharpe = strat.analyzers.getbyname("sharpe").get_analysis()
    analysis_trades = strat.analyzers.getbyname("trades").get_analysis()
    analysis_pyfolio = strat.analyzers.getbyname('pyfolio').get_pf_items()
    
    rtot = analysis_returns['rtot']
    rnorm = analysis_returns['rnorm']
    max_drawdown = analysis_drawdown['max']['drawdown'] if analysis_drawdown.get('max') else 0
    max_len = analysis_drawdown['max']['len'] if analysis_drawdown.get('max') else 0
    sharpe_ratio = analysis_sharpe['sharperatio']
    trades_total = analysis_trades['total']['total']
    winrate = analysis_trades['won']['total'] / trades_total if trades_total != 0 else 0
    returns, positions, transactions, gross_lev = analysis_pyfolio
    
    report_path = os.path.join(output_dir, "quantstats_report.html")
    qt.reports.html(
        returns=returns,
        output=report_path,
        title=STRATEGY_NAME,
        download_btn=True
    )
    logger.info(f"QuantStats HTML 报告已成功保存到: {report_path}")

    logger.info(f"总回报率 (rtot): {rtot}")
    logger.info(f"年化回报率 (rnorm): {rnorm}")
    logger.info(f"最大回撤 (max drawdown): {max_drawdown}%, 回撤长度：{max_len}")
    logger.info(f"夏普比率 (Sharpe): {sharpe_ratio}")
    logger.info(f"总交易数: {trades_total}")
    logger.info(f"胜率: {winrate}")
    logging.shutdown()
    
    cerebro.plot()



if __name__ == "__main__":
    run_backtest()
    