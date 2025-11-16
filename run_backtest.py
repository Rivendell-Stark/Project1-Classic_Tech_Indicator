'''
回测框架主文件
'''
import os
import logging
import pandas as pd

import backtrader as bt
import backtrader.feeds as btfeeds

from data import load_stock_data
from strategies import DMAStrategy, BuyonceStrategy
from utils import *


def run_backtest(strategy: bt.Strategy, strategy_params: dict, broker_params: dict, bt_analyzers:list):
    
    # --- A.1 初始化输出和日志 ---
    output_dir, logger = setup_logger(STRATEGY_NAME, START_DATE, END_DATE)
    print_and_log(f"回测开始: {STRATEGY_NAME}", logger=logger)
    print(f"回测结果保存路径: {output_dir}")

    # --- A.2 配置策略参数 ---
    params_log = ",".join([f"{k}={v}" for k,v in strategy_params.items()])
    print_and_log(f"回测策略参数: {params_log}", logger=logger)

    strategy_params['log_dir'] = output_dir

    # --- B. 加载数据 ---
    stock_data_dict = load_stock_data(DATA_POOL, START_DATE, END_DATE)

    if not stock_data_dict:
        print_and_log(f"加载股票代码 {DATA_POOL} 在 {START_DATE} ~ {END_DATE} 期间的数据失败, 回测结束", logger=logger, level=logging.ERROR)
        return
    
    # --- C. 配置 Cerebro ---
    cerebro = bt.Cerebro()

    # --- C.1 初始资金与费用设置 ---
    cerebro.broker.setcash(broker_params['cash'])
    cerebro.broker.setcommission(commission=broker_params['commission'])
    # cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # --- C.2 添加数据源 ---
    for code, df in stock_data_dict.items():
        data = btfeeds.PandasData(dataname=df, name=code)
        cerebro.adddata(data)

    # --- C.3 添加策略 ---
    cerebro.addstrategy(strategy, **strategy_params)

    # --- C.4 配置分析器 ---
    analyzers_list = bt_analyzers
    configure_analyzers(cerebro=cerebro, analyzers_list=analyzers_list)

    # --- C.5 配置交易记录 ---
    trades_path = os.path.join(output_dir, 'trades_records.csv')
    cerebro.addwriter(bt.WriterFile, csv=True, out=trades_path)

    # --- D. 运行回测 ---
    print_and_log("初始价值: %.2f" % cerebro.broker.getvalue(), logger=logger)
    results = cerebro.run()
    print_and_log('最终价值: %.2f' % cerebro.broker.getvalue(), logger=logger)

    # --- E. 回测结果分析 ---
    if not results:
        print_and_log("策略运行失败，无返回结果，回测结束", logger=logger)
        return
    
    strat = results[0]
    metrics, ret_series = generate_analysis(strat, analyzers_list)
    report_path = generate_quantstats_report(ret_series, output_dir, STRATEGY_NAME)

    if report_path:
        print_and_log(f"QuantStats HTML 报告已生成, 路径为： {report_path}", logger=logger)
    else:
        print_and_log("QuantStats HTML 报告生成失败。", logger=logger, level=logging.ERROR)

    # --- F. 控制台输出指标 ---
    metrics_formatted = format_float_output(metrics)
    print_and_log(f"总回报率 (rtot): { metrics_formatted['rtot']}", logger=logger)
    print_and_log(f"年化回报率 (rnorm): { metrics_formatted['rnorm']}", logger=logger)
    print_and_log(f"最大回撤 (MaxDD): { metrics_formatted['max_dd']}%, 回撤长度为:{ metrics_formatted['max_len']}", logger=logger)
    print_and_log(f"夏普比率 (Sharpe): { metrics_formatted['sharpe']}", logger=logger)
    print_and_log(f"总交易数 (total): { metrics_formatted['total']}", logger=logger)
    print_and_log(f"胜率 (winrate): { metrics_formatted['winrate']}", logger=logger)
    print("--------------------------------------")

    logging.shutdown()
    cerebro.plot()
    return

def run_opt(strategy: bt.Strategy ,opt_params: dict, opt_vars: list, broker_params: dict, opt_analyzers: list):
    # --- A. 初始化输出和日志 ---
    output_dir, logger = setup_logger_opt(STRATEGY_NAME, START_DATE, END_DATE)
    print_and_log(f"参数优化开始: {STRATEGY_NAME}", logger=logger)
    print(f"优化结果保存路径: {output_dir}")

    # --- B. 预加载数据 ---
    stock_data_dict = load_stock_data(DATA_POOL, START_DATE, END_DATE)

    if not stock_data_dict:
        print_and_log(f"加载股票代码 {DATA_POOL} 在 {START_DATE} ~ {END_DATE} 期间的数据失败, 优化结束", logger=logger, level=logging.ERROR)
        return None, output_dir
    
    # --- C. 生成参数组合 ---
    opt_dict = {}
    for optvar in opt_vars:
        opt_dict[optvar] = opt_params[optvar]
    constraints = opt_params.get("constraints")
    if not constraints:
        print_and_log(f"注意：优化参数组合没有约束条件", logger=logger, level=logging.WARNING)

    possible_combos = opt_param_combination(opt_dict, constraints)
    remains_params = {k: v for k, v in opt_params.items() if k not in opt_vars and k != "constraints"}

    # --- D. 遍历参数进行回测 ---
    all_results = []
    for combo in possible_combos:
        print_and_log(f"正在回测参数组合：{", ".join([f"{k}={v}" for k,v in combo.items()])}", logger=logger)

        # --- a. 配置 Cerebro ---
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(broker_params["cash"])
        cerebro.broker.setcommission(commission=broker_params["commission"])
        # cerebro.addsizer(bt.sizers.FixedSize, stake=1)

        # --- b. 添加数据源 ---
        for code, df in stock_data_dict.items():
            data = btfeeds.PandasData(dataname=df, name=code)
            cerebro.adddata(data)

        # --- c. 添加策略 ---
        cerebro.addstrategy(strategy, **combo, **remains_params, is_opt=True)

        # --- d. 配置分析器 ---
        analyzers_list = opt_analyzers
        configure_analyzers(cerebro=cerebro, analyzers_list=analyzers_list)

        # --- e. 运行回测 ---
        results = cerebro.run()    

        # --- f. 回测结果分析 ---
        if not results:
            print_and_log("本次回测运行失败，无结果", logger=logger, level=logging.ERROR)
            continue
            
        strat = results[0]
        metrics, _ = generate_analysis(strat, analyzers_list)
        bt_result = metrics | combo
        bt_result['combo'] = combo
        all_results.append(bt_result)
    
    # --- E. 格式化输出所有结果 ---
    print_and_log(f"优化完成", logger=logger)
    return pd.DataFrame(all_results), output_dir


if __name__ == "__main__":

    STRATEGY_NAME = 'DMAStrategy'
    DATA_POOL = ['600519']
    START_DATE = '2016-01-01'
    END_DATE = '2025-12-31'  
    
    broker_params = {
        'commission': 0.001,
        "cash": 1000000.0 
    }

    # --- 回测 ---
    strategy_params = {
        "fast": 15,
        "slow": 50,
        "loss_stop": 0.05,
        'target_pos': 0.95,
    }
    bt_analyzers = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer', 'PyFolio']

    run_backtest(DMAStrategy, strategy_params, broker_params, bt_analyzers)
    
    # --- 参数优化 ---
    opt_params = {
        "fast": range(5, 51, 5),
        "slow": range(10, 251, 10),
        "loss_stop": 0.05,
        'target_pos': 0.95,
        'constraints': ['fast < slow']
    }
    opt_vars = ['fast', 'slow']
    opt_analyzers = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer']

    # results_df, output_dir = run_opt(DMAStrategy, opt_params, opt_vars, broker_params, opt_analyzers)
    # best_sharpe_row = plot_heatmap(results_df, "sharpe", output_dir, 'fast', 'slow')
    # best_rtot_row = plot_heatmap(results_df, "rtot", output_dir, 'fast', 'slow')

    logging.shutdown()