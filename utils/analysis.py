import os
import time
import random
import logging

import backtrader as bt
import backtrader.analyzers as btanal

import quantstats as qt

ANALYZER_MAP = {
    'Returns': btanal.Returns,
    'DrawDown': btanal.DrawDown,
    'SharpeRatio': btanal.SharpeRatio,
    'TradeAnalyzer': btanal.TradeAnalyzer,
    'PyFolio': btanal.PyFolio,
    'TimeDrawDown': btanal.TimeDrawDown,
    'AnnualReturn': btanal.AnnualReturn,
    'VWR': btanal.VWR, 
    'SQN': btanal.SQN,
    'Calmar': btanal.Calmar,
    'GrossLeverage': btanal.GrossLeverage,
    'PositionsValue': btanal.PositionsValue,
    "LogReturnsRolling": btanal.LogReturnsRolling,
    "PeriodStats": btanal.PeriodStats,
    "SharpeRatio_A": btanal.SharpeRatio_A,
    "TimeReturn": btanal.TimeReturn,
    "Transactions": btanal.Transactions
}

def configure_analyzers(cerebro: bt.cerebro, analyzers_list: list) -> None:
    for name, AnalyzerClass in ANALYZER_MAP.items():
        if name in analyzers_list:
            cerebro.addanalyzer(AnalyzerClass, _name = name.lower())
    return 

def generate_analysis(strat, analyzers_list: list[str]):
    metrics = {}

    if "Returns" in analyzers_list:
        try:
            returns_ana = strat.analyzers.returns.get_analysis()
            metrics["rtot"] = returns_ana['rtot']
            metrics['rnorm'] = returns_ana['rnorm']
        except Exception as e:
            metrics['rtot'] = "N/A"
            metrics['rnorm'] = 'N/A'

    if "DrawDown" in analyzers_list:
        try:
            drawdown_ana = strat.analyzers.drawdown.get_analysis()
            metrics['max_dd'] = abs(drawdown_ana['max']['drawdown'])
            metrics['max_len'] = drawdown_ana['max']['len']
        except Exception as e:
            metrics['max_dd'] = "N/A"
            metrics['max_len'] = "N/A"
            
    
    if "SharpeRatio" in analyzers_list:
        try:
            sharpe_ana = strat.analyzers.sharperatio.get_analysis()
            metrics['sharpe'] = sharpe_ana['sharperatio']
        except Exception as e:
            metrics['sharpe'] = "N/A" 
    
    if "TradeAnalyzer" in analyzers_list:
        try:
            ta_ana = strat.analyzers.tradeanalyzer.get_analysis()
            metrics['total'] = ta_ana.get('total', {}).get('closed', 0)
            won_trades = ta_ana.get('won', {}).get('total', 0)
            metrics['winrate'] = won_trades / metrics['total'] if metrics['total'] > 0 else 'N/A'
        except Exception as e:
            metrics['total'] = "N/A"
            metrics['winrate'] = "N/A"

    if "PyFolio" in analyzers_list:
        try:
            ret_series, pos_series, transactions, gross_lev = strat.analyzers.pyfolio.get_pf_items()
        except Exception as e:
            return metrics, None
    else:
        ret_series = None

    return (metrics, ret_series)

def generate_quantstats_report(ret_series, output_dir, strategy_name, suffix: bool=False):
    """使用 QuantStats 生成 HTML 报告。"""

    if ret_series is None or ret_series.empty:
        return None
    
    if suffix:
        time_stamp = time.time_ns()
        rand = random.randint(0, 9)
        report_path = os.path.join(output_dir, f"QTreport_{time_stamp}_{rand}.html")
    else:
        report_path = os.path.join(output_dir, f"QTreport.html")

    qt.reports.html(
        returns=ret_series,
        output=report_path,
        title=strategy_name,
        download_btn=True
    )
    return report_path
