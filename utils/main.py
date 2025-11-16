import os
import time
import logging
from typing import Tuple, Optional, Iterable
from itertools import product

def make_filename(file_dir: str, *args: str, file_type: Optional[str] = None) -> str:
    """
    给定输出文件目录(file_dir)和希望文件名字里有的元素(*args),返回形如 "file_dir/AA_BB_CC_DD.filetype" 的文件路径。
    
    若file_type为None, 则可作为文件夹路径。
    """
    file_name = "_".join(args)
    file_name = file_name + f'.{file_type}' if file_type else file_name
    return os.path.join(file_dir, file_name)

def print_and_log(txt: str, logger: logging.Logger, level=logging.INFO):
    match level:
        case logging.INFO:
            logger.info(txt)
        case logging.WARNING:
            logger.warning(txt)
        case logging.ERROR:
            logger.error(txt)
    print(txt)

def format_float_output(dict: dict):
    for key, value in dict.items():
        if isinstance(value, float):
            dict[key] = '%.2f' % value
    return dict

def opt_param_combination(opt_dict: Iterable, constraints: list[str] = None) -> list[dict]:

    keys = list(opt_dict.keys())
    value_lists = list(opt_dict.values())
    value_combinations = list(product(*value_lists))
    all_combinations = [dict(zip(keys, combo)) for combo in value_combinations]

    if not constraints:
        return all_combinations

    filtered = []
    for combo in all_combinations:
        if all(eval(expr, {}, combo) for expr in constraints):
            filtered.append(combo)

    return filtered


def setup_logger(
        strategy_name: str, 
        start_date: str, 
        end_date: str
        ) -> Tuple[str, logging.Logger]:
    """
    Input: 策略名字、回测开始时间、回测结束时间
    
    Output: 日志目录(output_dir)、回测日志记录器对象(logger)
    """

    # 在 results 文件夹下创建 output_dir 文件夹 作为存放回测结果的文件夹
    timestamp = time.strftime(r'%H%M%S')
    output_dir = make_filename("results", "Backtest", strategy_name, start_date, end_date, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # 建立logger对象，并配置handler
    bt_logger = logging.getLogger('BacktestLogger')
    bt_logger.setLevel(logging.INFO)
    if bt_logger.handlers:
        bt_logger.handlers.clear()
    
    log_path = make_filename(output_dir, 'backtest_log', file_type="log")
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s')
    file_handler.setFormatter(formatter)
    
    bt_logger.addHandler(file_handler)

    # 返回结果，
    return output_dir, bt_logger

def setup_logger_opt(
        strategy_name: str, 
        start_date: str, 
        end_date: str
        ) -> Tuple[str, logging.Logger]:

    # 在 results 文件夹下创建 output_dir 文件夹 作为存放回测结果的文件夹
    timestamp = time.strftime(r'%H%M%S')
    output_dir = make_filename("results", "Optimization", strategy_name, start_date, end_date, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # 建立logger对象，并配置handler
    opt_logger = logging.getLogger('OptimizationLogger')
    opt_logger.setLevel(logging.INFO)
    if opt_logger.handlers:
        opt_logger.handlers.clear()
    
    log_path = make_filename(output_dir, 'optimization_log', file_type="log")
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s')
    file_handler.setFormatter(formatter)
    
    opt_logger.addHandler(file_handler)

    # 返回结果，
    return output_dir, opt_logger



