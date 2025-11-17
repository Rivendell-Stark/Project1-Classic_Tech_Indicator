from backtest import run_backtest, run_opt
from utils import plot_heatmap

from strategies import *


global_options = {
    "strategy_name": 'DMAStrategy',
    "data_pool": ['600519'],
    "start_date": "2016-01-01",
    "end_date": "2025-12-31",
    'commission': 0.001,
    "cash": 1000000.0 
}

def bt_DMA():
    # --- 回测 ---
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


def bt_RSI():
    pass

if __name__ == "__main__":

    bt_DMA()