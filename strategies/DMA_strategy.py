'''
策略: 单股票双均线择时策略

开仓信号: 金叉 + 无持仓
平仓信号: 死叉 + 有持仓
止损信号: 损失超过买入价的 loss_stop

待优化: 
    1. 过滤假信号(1%?, 0.5%?) 
    2. 收盘价 > 长均线， 确认趋势
    3. 三均线: 短中线生成信号，长线看趋势


'''
import backtrader.indicators as btind

from ._Base_Strategy import Strategy_withlog

class DMAStrategy(Strategy_withlog):
    # --- A. 策略参数设置 ---
    params = (
        ("fast", 15),
        ("slow", 50),
        ("loss_stop", 0.05),
        ('target_pos', 0.95),
        ('is_opt', False),
        )
    
    # --- B.1 策略初始化 ---
    def __init__(self):
        super().__init__()
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open

        self.fast_ma = btind.MovingAverageSimple(self.datas[0].close, period=self.p.fast, plot=True)
        self.slow_ma = btind.MovingAverageSimple(self.datas[0].close, period=self.p.slow, plot=True)
        self.cross_over = btind.CrossOver(self.fast_ma, self.slow_ma)


    # --- B.2 策略周期执行 ---
    def next(self):
        buy_sig = self.cross_over[0] > 0
        sell_sig = self.cross_over[0] < 0
        risk_sig = self.datas[0].low[0] <= (self.buyprice * (1.0 - self.p.loss_stop))

        if self.order:
            return

        if not self.position:
            if buy_sig:
                self.log(f"买入信号产生: 快线价格 {self.fast_ma[0]: .2f}, 慢线价格 {self.slow_ma[0]: .2f}")
                self.order = self.order_target_percent(target=self.p.target_pos)
        else:
            if sell_sig:
                self.log(f"卖出信号产生: 快线价格 {self.fast_ma[0]: .2f}, 慢线价格 {self.slow_ma[0]: .2f}")
                self.order = self.close()
            elif risk_sig:
                self.log(f"止损信号产生: 已损失{1-(self.datas[0].low[0]/self.buyprice): .2%}")
                self.order = self.close()