import os
import logging
import backtrader as bt

class Strategy_withlog(bt.Strategy):
    """
    为基础策略 bt.Strategy 添加记录日志功能。
    """
    params = (
        ('log_dir', None),
        ('is_opt', False)
    )

    def __init__(self):

        # --- 定义相关变量 ---
        self.buyprice = 0.0
        self.buycomm = 0.0
        self.order = None
        self.bar_executed = len(self)

        # --- 判断是否为优化模式
        if self.p.is_opt:
            return

        # --- 创建日志记录器 ---
        self.s_logger = logging.getLogger('StrategyLogger')
        if self.s_logger.handlers:
            self.s_logger.handlers.clear()

        # --- 配置记录器 ---
        log_path = os.path.join(self.p.log_dir, "details.log")
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(levelname)s | %(message)s'))
        self.s_logger.addHandler(file_handler)

        # --- 初始化日志记录 ---
        strategy_name = self.__class__.__name__
        params_str = ", ".join([f"{k}={v}" for k, v in self.p._getkwargs().items() if k not in ['log_dir'] and not k.startswith("_")])
        self.log(f"策略({strategy_name})初始化完成。数据源: {self.data._name}")
        self.log(f"策略参数: {params_str}")



    def log(self, txt, level=logging.INFO):

        if self.p.is_opt:
            return

        dt = self.datas[0].datetime.date(0)
        logline = f"[{self.data._name}] {dt.isoformat()} | {txt}]"
        
        match level:
            case logging.INFO:
                self.s_logger.info(logline)
            case logging.WARNING:
                self.s_logger.warning(logline)
            case logging.ERROR:
                self.s_logger.error(logline)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("买入订单执行, 价格:%.2f, 成本: %.2f, 佣金费用: %.2f" % 
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            elif order.issell():
                self.log("卖出订单执行, 价格: %.2f, 成本: %.2f, 佣金费用: %.2f" %
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单执行失败: {order.getstatusname()}', level=logging.WARNING)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'交易关闭 - 记录盈亏: 毛利润 {trade.pnl:.2f}, 净利润 {trade.pnlcomm:.2f}')
        
    def stop(self):
        self.log(f"{self.data._name} 策略记录完毕。")