import pandas as pd

from backtest import run_backtest, run_opt
from utils import plot_heatmap, opt_output_result
from strategies import *


def bt_DMA():
    # --- 回测 ---
    global_options = {
    "strategy_name": 'DMAStrategy',
    "data_pool": ['600519'],
    "start_date": "2016-01-01",
    "end_date": "2025-12-31",
    'commission': 0.001,
    "cash": 1000000.0 
    }
    
    strategy_params = {
        "fast": 15,
        "slow": 50,
        "loss_stop": 0.05,
        'target_pos': 0.95,
    }
    bt_analyzers = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer', 'PyFolio']

    run_backtest(DMAStrategy, strategy_params, global_options, bt_analyzers)

def opt_DMA():
    # --- 参数优化 ---
    global_options = {
    "strategy_name": 'DMAStrategy',
    "data_pool": ['600519'],
    "start_date": "2016-01-01",
    "end_date": "2025-12-31",
    'commission': 0.001,
    "cash": 1000000.0 
    }
    opt_params = {
        "fast": range(5, 51, 5),
        "slow": range(10, 251, 10),
        "loss_stop": 0.05,
        'target_pos': 0.95,
        'constraints': ['fast < slow']
    }
    opt_vars = ['fast', 'slow']
    opt_analyzers = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer']

    results_df, output_dir = run_opt(DMAStrategy, opt_params, opt_vars, global_options, opt_analyzers)
    best_sharpe_row = plot_heatmap(results_df, "sharpe", output_dir, 'fast', 'slow')
    best_rtot_row = plot_heatmap(results_df, "rtot", output_dir, 'fast', 'slow')

def bt_RSI_Reversal():
    global_options = {
    "strategy_name": 'RSI_Reversal_Strategy',
    "data_pool": ['600519'],
    "start_date": "2016-01-01",
    "end_date": "2025-12-31",
    'commission': 0.001,
    "cash": 1000000.0 
    }
    strategy_params = {
        "period": 14,
        "low_level": 40,
        "high_level": 70,
        "sma_period": 30,
        "lma_period": 200,
        "atr_period": 14,
        "atr_multiplier": 2.0,
        'target_pos': 0.95,
    }
    bt_analyzers = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer', 'PyFolio']
    run_backtest(RSI_Reversal_Strategy, strategy_params, global_options, bt_analyzers)

def opt_RSI_Reversal():
    global_options = {
    "strategy_name": 'RSI_Reversal_Strategy',
    "data_pool": ['600519'],
    "start_date": "2016-01-01",
    "end_date": "2025-12-31",
    'commission': 0.001,
    "cash": 1000000.0 
    }
    opt_params = {
        "period": [9,14,21],
        "low_level": [30,35,40],
        "high_level": 70,
        "sma_period": [20,30,35],
        "lma_period": [120,150,200],
        "atr_period": 14,
        "atr_multiplier": [1.5,2.0,2.5,3.0],
        'target_pos': 0.95,
    }
    opt_vars = ["period", "low_level", "sma_period","lma_period","atr_multiplier"]
    opt_analyzers = ["Returns", "DrawDown", "SharpeRatio"]

    results_df, output_dir = run_opt(RSI_Reversal_Strategy, opt_params, opt_vars, global_options, opt_analyzers)
    opt_output_result(results_df, output_dir)

def bt_RSI_Trend():
    global_options = {
    "strategy_name": 'RSI_Reversal_Strategy',
    "data_pool": ['600519'],
    "start_date": "2016-01-01",
    "end_date": "2025-12-31",
    'commission': 0.001,
    "cash": 1000000.0 
    }
    strategy_params = {
        "period": 14,
        "low_level": 60,
        "high_level": 70,
        "lma_period": 100,
        "atr_period": 14,
        "atr_multiplier": 2.0,
        'target_pos': 0.95,
    }
    bt_analyzers = ["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer', 'PyFolio']
    run_backtest(RSI_Trend_Strategy, strategy_params, global_options, bt_analyzers)

def opt_RSI_Trend():
    global_options = {
    "strategy_name": 'RSI_Reversal_Strategy',
    "data_pool": ['600519'],
    "start_date": "2016-01-01",
    "end_date": "2025-12-31",
    'commission': 0.001,
    "cash": 1000000.0 
    }
    opt_params = {
        "period": 14,
        "low_level": range(30,61,5),
        "high_level": range(50,81,5),
        "lma_period": 100,
        "atr_period": 14,
        "atr_multiplier": 2.0,
        'target_pos': 0.95,
        "constraints": ['low_level <= high_level']
    }
    opt_vars = ["low_level", "high_level"]
    opt_analyzers = ["Returns", "DrawDown", "SharpeRatio"]

    results_df, output_dir = run_opt(RSI_Reversal_Strategy, opt_params, opt_vars, global_options, opt_analyzers)
    opt_output_result(results_df, output_dir)
    plot_heatmap(results_df, "rtot", output_dir, "low_level", "high_level")

if __name__ == "__main__":

    bt_RSI_Trend()