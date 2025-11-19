'''
策略: RSI策略

RSI 指标用于衡量一段时间内价格上涨的强度与下跌的强度之比，介于 0 到 100 之间。
RSI > 50: 市场动量偏向于多头（上涨）。
RSI < 50: 市场动量偏向于空头（下跌）。

|  区域 |  RSI 值  |                 市场含义                |
| ----- | -------- | -------------------------------------- |
| 超买区 | 70 ~ 100 | 价格在短期内上涨过快，可能面临回调或反转。 |
| 超卖区 | 0 ~ 30   | 价格在短期内下跌过快，可能面临反弹或反转。 |
| 中立区 | 30 ~ 70  | 市场处于正常波动，无明显单边超买超卖状态。 |

A. 均值回归（反转）策略
买入信号：当 RSI 跌破 30（进入超卖区）后，重新向上突破 30 时，视为买入信号。
卖出信号: 当 RSI 升破 70（进入超买区）后，重新向下跌破 70 时，视为卖出信号。

优化：
趋势过滤：只在确认牛市的市场中买入，确认短期上涨动能耗尽时卖出
止损指标：由ATR指标替代固定的止损比例


B. 趋势确认（顺势）策略
买入信号：股票处于明确的上升趋势中，当 RSI 回落至 40~50 区间时，视为买入（回调结束）信号。
卖出信号：股票处于明确的下降趋势中，当 RSI 反弹至 50~60 区间时，视为卖出（反弹结束）信号。

优化:
RSI过滤：当rsi超过10日均线时，即确认上涨趋势，再买入。


'''
import backtrader.indicators as btind
from ._Base_Strategy import Strategy_withlog

class RSI_Reversal_Strategy(Strategy_withlog):
    # --- A. 策略参数设置 ---
    params = (
        ("period", 14),
        ("low_level", 30),
        ("high_level", 70),
        ("sma_period", 10),
        ("lma_period", 200),
        ("atr_period", 14),
        ("atr_multiplier", 2.0),
        ('target_pos', 0.95),
        ('is_opt', False),
        )
    
    # --- B.1 策略初始化 ---
    def __init__(self):
        super().__init__()
        self.dataclose = self.datas[0].close
        self.rsi = btind.RelativeStrengthIndex(self.datas[0], period=self.p.period)

        self.lma = btind.MovingAverageSimple(self.datas[0].close, period=self.p.lma_period)
        self.sma = btind.MovingAverageSimple(self.datas[0].close, period=self.p.sma_period)
        self.atr = btind.AverageTrueRange(self.datas[0], period=self.p.atr_period)
        
        self.stopprice = 0.0

    def notify_order(self, order):

        super().notify_order(order)

        if order.status == order.Completed and order.isbuy():
            current_atr = self.atr[0]
            self.stopprice = self.buyprice - (self.p.atr_multiplier * current_atr)
            self.log(f"ATR 止损价设置为: {self.stopprice:,.2f} (买入价 {self.buyprice:,.2f} - {self.p.atr_multiplier} x ATR {current_atr:,.2f})")

    # --- B.2 策略周期执行 ---
    def next(self):
        buy_sig = self.rsi[0] > self.p.low_level and self.rsi[-1] <= self.p.low_level
        sell_sig = self.rsi[0] < self.p.high_level and self.rsi[-1] >= self.p.high_level
        ltrend_sig = self.dataclose[0] > self.lma[0]
        strend_sig = self.dataclose[0] < self.sma[0]
        risk_sig = self.datas[0].low[0] <= self.stopprice

        if self.order:
            return

        if not self.position:
            if buy_sig and ltrend_sig:
                self.log(f"买入信号产生: RSI 上期值 {self.rsi[-1]: .2f}, 当期值 {self.rsi[0]:.2f}")
                self.order = self.order_target_percent(target=self.p.target_pos)
        else:
            if sell_sig and strend_sig:
                self.log(f"卖出信号产生: RSI 上期值 {self.rsi[-1]: .2f}, 当期值 {self.rsi[0]:.2f}")
                self.order = self.close()
            elif risk_sig:
                loss_percent = 1 - (self.datas[0].low[0] / self.buyprice)
                self.log(f"ATR 止损信号产生: 当前最低价 {self.datas[0].low[0]: .2f}, 低于止损价 {self.stopprice: .2f}。已损失 {loss_percent:.2%}")
                self.order = self.close()


class RSI_Trend_Strategy(Strategy_withlog):
    # --- A. 策略参数设置 ---
    params = (
        ("period", 14),
        ("high_level", 60), # 动量确认买入阈值
        ("low_level", 50),  # 动量衰竭卖出阈值
        ("lma_period", 200), # 长期趋势过滤周期
        ("sma_period", 20),
        ("rsima_period",10),
        ('target_pos', 0.95),
        ("atr_period", 14),
        ("atr_multiplier", 2.0),
        ('is_opt', False),
    )

     # --- B.1 策略初始化 ---
    def __init__(self):
        super().__init__()
        self.dataclose = self.datas[0].close
        self.rsi = btind.RelativeStrengthIndex(self.datas[0], period=self.p.period)
        self.lma = btind.MovingAverageSimple(self.dataclose, period=self.p.lma_period)
        self.sma = btind.MovingAverageSimple(self.dataclose, period=self.p.sma_period)
        self.rsi_ma = btind.MovingAverageSimple(self.rsi, period=self.p.rsima_period)

        
        
        self.atr = btind.AverageTrueRange(self.datas[0], period=self.p.atr_period)
        self.stopprice = 0.0

    def notify_order(self, order):

        super().notify_order(order)

        if order.status == order.Completed and order.isbuy():
            current_atr = self.atr[0]
            self.stopprice = self.buyprice - (self.p.atr_multiplier * current_atr)
            self.log(f"ATR 止损价设置为: {self.stopprice:,.2f} (买入价 {self.buyprice:,.2f} - {self.p.atr_multiplier} x ATR {current_atr:,.2f})")


    # --- B.2 策略周期执行 ---
    def next(self):
        if self.order:
            return
        
        buy_sig = self.rsi[0] > self.p.high_level and self.rsi[-1] <= self.p.high_level and self.rsi[0] > self.rsi_ma[0]
        sell_sig = self.rsi[0] < self.p.low_level and self.rsi[-1] >= self.p.low_level  and self.rsi[0] < self.rsi_ma[0]
        ltrend_sig = self.dataclose[0] > self.lma[0]
        strend_sig = self.dataclose[0] < self.sma[0]
        risk_sig = self.datas[0].low[0] <= self.stopprice

        if self.dataclose[0] == self.datas[0].high[-1]:
            new_stopprice = self.dataclose[0] - (self.atr[0] * self.p.atr_multiplier)
            self.stopprice = max(new_stopprice, self.stopprice)
            self.log(f"由于趋势上涨，止损价更新为{self.stopprice}")

        if not self.position:
            if buy_sig and ltrend_sig:
                self.log(f"买入信号产生: RSI 上期值 {self.rsi[-1]: .2f}, 当期值 {self.rsi[0]:.2f}")
                self.order = self.order_target_percent(target=self.p.target_pos)
        else:
            if sell_sig:
                self.log(f"卖出信号产生: RSI 上期值 {self.rsi[-1]: .2f}, 当期值 {self.rsi[0]:.2f}")
                self.order = self.close()
            elif risk_sig:
                loss_percent = 1 - (self.datas[0].low[0] / self.buyprice)
                self.log(f"ATR 止损信号产生: 当前最低价 {self.datas[0].low[0]: .2f}, 低于止损价 {self.stopprice: .2f}。已损失 {loss_percent:.2%}")
                self.order = self.close()