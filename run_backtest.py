'''
回测框架主文件
'''

from __future__ import (absolute_import, division, print_function, unicode_literals)  

import os
import time
import logging

from datetime import datetime
import pandas as pd
import numpy as np
import quantstats as qt
import pyfolio as pf

import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanal
import backtrader.indicators as btind

from data import load_stock_data
from strategies import DMAStrategy
from utils import *

# --- 1. 配置 ---
STRATEGY_NAME = 'DMA_Strategy'
# DATA_POOL = ['600519','601318','000333','300751']
DATA_POOL = ['600519']
START_DATE = datetime(2016,1,1).strftime(r'%Y-%m-%d')
END_DATE = datetime(2025,12,31).strftime(r'%Y-%m-%d')

def run_backtest(stock_code, strategy, params):
    
    # --- A.1 初始化输出和日志 ---
    output_dir, logger = setup_output_run(STRATEGY_NAME, START_DATE, END_DATE)
    logger.info(f"回测开始: {STRATEGY_NAME}")
    logger.info(f"回测结果保存路径: {output_dir}")

    # --- A.2 配置策略参数 ---
    strategy_params = {
        "fast": 20,
        "slow": 60,
        "loss_stop": 0.05,
        'target_pos': 0.95,
        'log_dir': output_dir,
        'sys_logger': logger
    }
    params_log = ",".join([f"{k}={v}" for k,v in strategy_params.items() if k not in ['log_dir', 'sys_logger']])
    logger.info(f"回测策略参数: {params_log}")

    # --- B. 加载数据 ---
    stock_data_dict = load_stock_data(DATA_POOL, START_DATE, END_DATE)

    if not stock_data_dict:
        logger.error(f"加载数据失败")
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
    cerebro.addstrategy(DMAStrategy, **strategy_params)

    # --- C.4 配置分析器 ---
    analyzers_list = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer', 'PyFolio']
    configure_analyzers(cerebro=cerebro, analyzers_list=analyzers_list)

    # --- C.5 配置交易记录 ---
    trades_path = os.path.join(output_dir, 'trades_records.csv')
    cerebro.addwriter(bt.WriterFile, csv=True, out=trades_path)

    # --- D. 运行回测 ---
    print("初始价值: %.2f" % cerebro.broker.getvalue())
    results = cerebro.run()    
    print('最终价值: %.2f' % cerebro.broker.getvalue())

    # --- E. 回测结果分析 ---
    if not results:
        logger.error("回测失败，无结果")
        return
    strat = results[0]
    metrics, ret_series = generate_analysis(strat, analyzers_list, logger)
    generate_quantstats_report(ret_series, output_dir, STRATEGY_NAME, logger)

    # --- F. 控制台输出指标 ---
    print(f"总回报率 (rtot): {metrics['rtot']:.2%}")
    print(f"年化回报率 (rnorm): {metrics['rnorm']:.2%}")
    print(f"最大回撤 (MaxDD): {metrics['max_dd']:.2f}%, 回撤长度为:{metrics['max_len']}")
    print(f"夏普比率 (Sharpe): {metrics['sharpe']:.2f}")
    print(f"总交易数 (total): {metrics['total']}")
    print(f"胜率 (winrate): {metrics['winrate']: .2%}")
    print("--------------------------------------")

    logging.shutdown()
    # cerebro.plot()

    return metrics, ret_series

if __name__ == "__main__":
    run_backtest()
    