import os
import time
import logging
from datetime import datetime
from typing import Tuple, Any

# --- 配置 ---
RESULTS_BASE_DIR = 'results'


# --- 运行与结果分析类 ---
def setup_output_run(
        strategy_name: str, 
        start_date: str, 
        end_date: str
        ) -> Tuple[str, logging.Logger]:
    """
    1. 创建本次回测的唯一输出目录。
    2. 配置并返回一个专用的日志对象。

    返回：(输出目录路径, Logger对象)
    """

    # 构造并创建日志目录
    start_str = start_date
    end_str = end_date
    timestamp = time.strftime(r'%H%M%S')
    run_dir_name = f'{strategy_name}_{start_str}_{end_str}_{timestamp}'
    output_dir = os.path.join(RESULTS_BASE_DIR, run_dir_name)
    os.makedirs(output_dir, exist_ok=True)

    # 配置诊断日志
    log_path = os.path.join(output_dir, 'run_log.log')

    logger = logging.getLogger('BacktestLogger')
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return output_dir, logger

def report_run_summary(logger, metrics):
    """
    接收 logger 和关键指标字典，将最终的夏普比率、最大回撤等信息打印到日志和控制台。
    """
    pass

# --- 系统与数据状态检查类 ---
def check_prerequisites():
    """
    环境和连接检查: 数据库能连接、表存在、python库安装
    """
    pass

def validate_data_integrity():
    """
    数据有效性检查: NaN值是否存在, 日期是否连续
    """
    pass

def convert_format():
    """
    变量格式转换
    """
    pass

def convert_date_to_str(date_obj: Any, format: str = "%Y-%m-%d") -> str:
    """将 datetime 或 date 对象转换为 'YYYY-MM-DD' 字符串。"""
    if isinstance(date_obj, str):
        return date_obj 
    return date_obj.strftime(format)

# --- Backtrader 结果解析类 ---
def extract_returns_series(results):
    """
    从 Backtrader 的 Returns 分析器中提取日收益率序列
    """
    returns_analyzer = results[0].analyzers.returns.get_analysis()

    if 'rtn' in returns_analyzer:
        returns_series = returns_analyzer['rtn']
        returns_series.index = pd.to_datetime(returns_series.index)
        return returns_series
    
    raise KeyError("无法在 Backtrader Returns 分析器中找到 'rtn' 键。请检查分析器配置。")

def extract_analyzer_metrics(results):
    """
    从多个分析器（Sharpe Ratio, Max Drawdown, Total Trades）中提取数值，返回一个易于打印的字典或 Pandas Series
    """
    pass

