import logging
import os

import pandas as pd
import numpy as np
from typing import Dict, Any

import backtrader as bt
import backtrader.indicators as btind
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
    'PositionsValue': btanal.PositionsValue
}

def configure_analyzers(cerebro: bt.cerebro, analyzers_list: list=["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer', 'PyFolio']) -> None:

    for name, AnalyzerClass in ANALYZER_MAP.items():
        if name in analyzers_list:
            cerebro.addanalyzer(AnalyzerClass, _name = name.lower())
    return 

def generate_analysis(strat, analyzers_list, logger):
    metrics = {}

    if "Returns" in analyzers_list:
        try:
            returns_ana = strat.analyzers.returns.get_analysis()
            metrics["rtot"] = returns_ana['rtot']
            metrics['rnorm'] = returns_ana['rnorm']
            logger.info(f"总回报率 (rtot): {metrics["rtot"]}")
            logger.info(f"年化回报率 (rnorm): {metrics['rnorm']}")
        except Exception as e:
            logger.error(f"Returns 分析器提取失败: {e}")
            metrics['rtot'] = "N/A"
            metrics['rnorm'] = 'N/A'

    if "DrawDown" in analyzers_list:
        try:
            drawdown_ana = strat.analyzers.drawdown.get_analysis()
            metrics['max_dd'] = abs(drawdown_ana['max']['drawdown'])
            metrics['max_len'] = drawdown_ana['max']['len']
            logger.info(f"最大回撤 (max drawdown): {metrics['max_dd']}, 回撤长度：{metrics['max_len']}")
        except Exception as e:
            logger.error(f"DrawDown 分析器提取失败: {e}")
            metrics['max_dd'] = "N/A"
            metrics['max_len'] = "N/A"
            
    
    if "SharpeRatio" in analyzers_list:
        try:
            sharpe_ana = strat.analyzers.sharperatio.get_analysis()
            metrics['sharpe'] = sharpe_ana['sharperatio']
            logger.info(f"夏普比率 (Sharpe): {metrics['sharpe']: .2%}")
        except Exception as e:
            logger.error(f"SharpeRatio 分析器提取失败: {e}")
            metrics['sharpe'] = "N/A" 
    
    if "TradeAnalyzer" in analyzers_list:
        try:
            ta_ana = strat.analyzers.tradeanalyzer.get_analysis()
            metrics['total'] = ta_ana.get('total', {}).get('closed', 0)
            won_trades = ta_ana.get('won', {}).get('total', 0)
            metrics['winrate'] = won_trades / metrics['total'] if metrics['total'] > 0 else 'N/A'
        except Exception as e:
            logger.error(f"TradeAnalyzer 分析器提取失败: {e}")
            metrics['total'] = "N/A"
            metrics['winrate'] = "N/A"

    if "PyFolio" in analyzers_list:
        try:
            ret_series, pos_series, transactions, gross_lev = strat.analyzers.pyfolio.get_pf_items()
        except Exception as e:
            logger.error(f"PyFolio 收益率序列提取失败， 无法生成报告：{e}")
            return metrics, None
    else:
        ret_series = None

    return (metrics, ret_series)

def generate_quantstats_report(ret_series, output_dir, strategy_name, logger):
    """使用 QuantStats 生成 HTML 报告。"""

    if ret_series is None or ret_series.empty:
        logger.warning("收益率序列为空或不存在，跳过报告生成。")
        return
    
    report_path = os.path.join(output_dir, "quantstats_report.html")

    qt.reports.html(
        returns=ret_series,
        output=report_path,
        title=strategy_name,
        download_btn=True
    )
    logger.info(f"QuantStats HTML 报告已成功保存到: {report_path}")
    return report_path
