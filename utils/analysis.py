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

METRIC_EXTRACTION_MAP = {
    'Returns': [('rtor', ['rtot']),
                ('rnorm', ['rnorm'])],
    'DrawDown': [('max_drawdown', ['max','drawdown']),
                 ('max_len', ['max','len'])],
    'SharpeRatio': [("sharpe_ratio", ["sharperatio"])],
    'TradeAnalyzer': [],
    'PyFolio': [],
    'TimeDrawDown': [],
    'AnnualReturn': [('annual_return_dict', ['annual'])],
    'VWR': [('vwr', ['vmr'])], 
    'SQN':[('sqn', ['sqn'])],
    'Calmar': [('calmar_ratio', ['calmarratio'])],
    'GrossLeverage': [],
    'PositionsValue': [('final_positions_value', ['total'])]
}

def configure_analyzers(cerebro: bt.cerebro, analyzers_list: list=["Returns", "DrawDown", "SharpeRatio", 'TradeAnalyzer', 'PyFolio']) -> None:

    for name, AnalyzerClass in ANALYZER_MAP.items():
        if name in analyzers_list:
            cerebro.addanalyzer(AnalyzerClass, _name = name.lower())
    return 

def generate_analysis(strat, analyzers_list, logger):
    """
    动态提取指定分析器中的关键指标，并返回收益率序列。
    
    Args:
        strat (Strategy): 回测运行后的策略实例结果 (results[0])
        analyzers_list (list): 运行 configure_analyzers 时使用的列表。
        logger (Logger): 日志记录器。

    Returns:
        tuple: (metrics_dict, returns_series)
    """

    metrics = {}

    for analyzer_name in analyzers_list:
        if (analyzer_name in strat.analyzers) and (analyzer_name in METRIC_EXTRACTION_MAP):
            analyzer_instance = strat.analyzers.getbyname(analyzer_name.lower())            
            analysis_dict = analyzer_instance.get_analysis()
            
            for metric_key, dict_path in METRIC_EXTRACTION_MAP[analyzer_name]:
                current_value = analysis_dict
                extrated_value = 'N/A'
                
                try:
                    for key in dict_path:
                        current_value = current_value[key]
                    extrated_value = current_value
                except (KeyError, IndexError, TypeError) as e:
                    logger.error(f":指标 {metric_key} 不存在或提取错误：{e}")
                    extrated_value = 'N/A'

                metrics[metric_key] = extrated_value
    
    if ("TradeAnalyzer" in analyzers_list) and (metrics.get('total_trades') not in [0, 'N/A']):
        total_trades = metrics['total_trades']
        won_trades = metrics.get('won_trades', 0)
        winrate = won_trades / total_trades
    else:
        metrics['winrate'] = 'N/A'

    if "Returns" in analyzers_list:
        rtot = metrics.get("rtot", 'N/A')
        rnorm = metrics.get('rnorm', 'N/A')
        logger.info(f"总回报率 (rtot): {rtot}")
        logger.info(f"年化回报率 (rnorm): {rnorm}")

    if "DrawDown" in analyzers_list:
        max_drawdown = metrics.get('max_drawdown', 'N/A')
        max_len = metrics.get('max_len', 'N/A')
        logger.info(f"最大回撤 (max drawdown): {max_drawdown}%, 回撤长度：{max_len}")
    
    if "SharpeRatio" in analyzers_list:
        sharpe_ratio = metrics.get('sharpe_ratio', 'N/A')
        logger.info(f"夏普比率 (Sharpe): {sharpe_ratio}")

    if "TradeAnalyzer" in analyzers_list:
        trades_total = metrics.get('total_trades', 'N/A')
        winrate = metrics.get('winrate', 'N/A')
        logger.info(f"总交易数: {trades_total}")
        logger.info(f"胜率: {winrate}")

    try:
        ret_series, pos_series, transactions, gross_lev = strat.analyzers.pyfolio.get_pf_items()
    except Exception as e:
        logger.error(f"PyFolio 收益率序列提取失败， 无法生成报告：{e}")
        return metrics, None

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
