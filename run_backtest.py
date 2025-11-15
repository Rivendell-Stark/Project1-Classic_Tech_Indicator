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
import matplotlib.pyplot as plt
import quantstats as qt
import pyfolio as pf
import seaborn as sns

import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanal
import backtrader.indicators as btind

from data import load_stock_data
from strategies import DMAStrategy, BuyonceStrategy
from utils import *

# --- 1. 配置 ---

# DATA_POOL = ['600519','601318','000333','300751']



def run_backtest(strategy: bt.Strategy, params: dict):
    
    # --- A.1 初始化输出和日志 ---
    output_dir, logger = setup_output_run(STRATEGY_NAME, START_DATE, END_DATE)
    logger.info(f"回测开始: {STRATEGY_NAME}")
    logger.info(f"回测结果保存路径: {output_dir}")

    # --- A.2 配置策略参数 ---
    strategy_params = params
    params_log = ",".join([f"{k}={v}" for k,v in strategy_params.items()])
    logger.info(f"回测策略参数: {params_log}")

    strategy_params['log_dir'] = output_dir
    strategy_params['sys_logger'] = logger

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
    cerebro.addstrategy(strategy, **strategy_params)

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
        return None, None
    strat = results[0]
    metrics, ret_series = generate_analysis(strat, analyzers_list, logger)
    generate_quantstats_report(ret_series, output_dir, STRATEGY_NAME, logger)

    # --- F. 控制台输出指标 ---
    print(f"总回报率 (rtot): {metrics['rtot']}")
    print(f"年化回报率 (rnorm): {metrics['rnorm']}")
    print(f"最大回撤 (MaxDD): {metrics['max_dd']}%, 回撤长度为:{metrics['max_len']}")
    print(f"夏普比率 (Sharpe): {metrics['sharpe']}")
    print(f"总交易数 (total): {metrics['total']}")
    print(f"胜率 (winrate): {metrics['winrate']}")
    print("--------------------------------------")

    logging.shutdown()
    cerebro.plot()

    return metrics, ret_series

def run_opt(strategy: bt.Strategy, params: dict):
    # --- A.1 初始化输出和日志 ---
    OPT_STRATEGY_NAME = STRATEGY_NAME + "_Opt"
    output_dir, logger = setup_output_run(OPT_STRATEGY_NAME, START_DATE, END_DATE)
    logger.info(f"参数优化开始: {STRATEGY_NAME}")
    logger.info(f"优化结果保存路径: {output_dir}")
    
    silent_logger = logging.getLogger('SilentOptLogger')
    silent_logger.setLevel(logging.ERROR)

    # --- A.2 设置参数空间 ---
    fast_periods = range(5, 31, 5)
    slow_periods = range(20, 101, 10)
    all_results = []

    # --- A.3 预加载数据 ---
    stock_data_dict = load_stock_data(DATA_POOL, START_DATE, END_DATE)

    if not stock_data_dict:
        logger.error(f"加载数据失败, 优化终止")
        print("未读取到有效数据...")
        return pd.DataFrame()
    
    # --- B. 遍历参数进行回测 ---
    for fast in fast_periods:
        for slow in slow_periods:
            if fast > slow:
                continue
        
            logger.info(f"正在回测参数组合: fast={fast}, slow={slow}")
            print(f"正在回测参数组合: fast={fast}, slow={slow}")

            # --- C. 配置 Cerebro ---
            cerebro = bt.Cerebro()
            cerebro.broker.setcash(1000000.0)
            cerebro.broker.setcommission(commission=0.001)
            # cerebro.addsizer(bt.sizers.FixedSize, stake=1)

            # --- C.2 添加数据源 ---
            for code, df in stock_data_dict.items():
                data = btfeeds.PandasData(dataname=df, name=code)
                cerebro.adddata(data)

            # --- C.3 添加策略 ---
            strategy_params =  params.update({
                    "fast": fast,
                    "slow": slow,
                    'is_opt': True,       # 告知策略处于优化模式
                    'log_dir': None,      # 明确告诉 BaseStrategy 不写文件
                    'sys_logger': silent_logger # 传递静默 logger
                })
            cerebro.addstrategy(strategy, **strategy_params)

            # --- C.4 配置分析器 ---
            analyzers_list = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer']
            configure_analyzers(cerebro=cerebro, analyzers_list=analyzers_list)

            # --- D. 运行回测 ---
            results = cerebro.run()    

            # --- E. 回测结果分析 ---
            if not results:
                logger.error("本次测试失败，无结果")
                continue
                
            strat = results[0]
            metrics, _ = generate_analysis(strat, analyzers_list, silent_logger)
            metrics['fast'] = fast
            metrics['slow'] = slow

            if metrics.get('sharpe') not in [None, 'N/A']:
                all_results.append(metrics)
                # 记录到优化日志中
                logger.info(f"  -> Sharpe={metrics['sharpe']:.4f}, Rtot={metrics['rtot']:.2%}")
            else:
                logger.warning(f"  -> {fast}/{slow} Sharpe Ratio 无效，跳过。")

    logger.info("参数优化完成, 开始生成热力图")
    df_results = pd.DataFrame(all_results)

    if not df_results.empty:
        plot_heatmap(df_results, "sharpe", output_dir)
        plot_heatmap(df_results, 'rtot', output_dir)
    else:
        print("未生成有效回测结果，无法绘制热力图。")
        logger.error("未生成有效回测结果，无法绘制热力图。")

    logging.shutdown()
    return df_results


if __name__ == "__main__":

    STRATEGY_NAME = 'BuyOnceStrategy'
    DATA_POOL = ['600519']
    START_DATE = datetime(2016,1,1).strftime(r'%Y-%m-%d')
    END_DATE = datetime(2025,12,31).strftime(r'%Y-%m-%d')  
    
    strategy_params = {
        # "fast": 15,
        # "slow": 50,
        # "loss_stop": 0.05,
        'target_pos': 0.95,
    }

    run_backtest(BuyonceStrategy, strategy_params)
    
    opt_params = {
        "loss_stop": 0.05,
        'target_pos': 0.95,
    }
    
    
    # run_opt(BuyonceStrategy, opt_params)