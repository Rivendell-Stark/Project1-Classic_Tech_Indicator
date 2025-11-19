'''
布林带：
中轨线 (Middle Band, MID)： 价格的 N 周期简单移动平均线 (SMA)。
上轨线 (Upper Band, TOP)： 中轨线 + K 倍的标准差。
下轨线 (Lower Band, BOT)： 中轨线 - K 倍的标准差。

逻辑： 均值回归
买入 (Entry)：价格跌破下轨线 (BOT),市场处于超卖状态，准备买入等待价格反弹。
卖出 (Exit)：价格升穿上轨线 (TOP),市场处于超买状态，平仓获利，等待价格回归。

适用范围：
震荡盘整市 (Ranging / Sideways Market)：价格围绕中轨波动，没有明显的方向性趋势。
'''
import backtrader.indicators as btind
from ._Base_Strategy import Strategy_withlog


class Bollinger_Strategy(Strategy_withlog):
    params = (
        ('period', 20),           # 布林带周期
        ("devfactor", 2.0),       # 标准差倍数 K
        ("lma_period", 100),
        ("atr_period", 14),
        ("atr_multiplier", 2.0),
        ('target_pos', 0.95),
        ('is_opt', False),  
    )

    def __init__(self):
        super().__init__()
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low

        self.bbands = btind.BollingerBands(self.datas[0], period=self.p.period, devfactor=self.p.devfactor)
        self.upper_band = self.bbands.top
        self.lower_band = self.bbands.bot        
        self.atr = btind.AverageTrueRange(self.datas[0], period=self.p.atr_period)
        self.lma = btind.MovingAverageSimple(self.dataclose, period=self.p.lma_period)
        self.lmama = btind.MovingAverageSimple(self.lma, period=10)

        self.stopprice = 0.0

    def notify_order(self, order):
        super().notify_order(order)

        if order.status == order.Completed and order.isbuy():
            current_atr = self.atr[0]
            self.stopprice = self.buyprice - (self.p.atr_multiplier * current_atr)
            self.log(f"ATR 止损价设置为: {self.stopprice:,.2f} (买入价 {self.buyprice:,.2f} - {self.p.atr_multiplier} x ATR {current_atr:,.2f})")

    def next(self):
        if self.order:
            return
        
        buy_sig = self.dataclose[0] < self.bbands.bot[0]
        sell_sig = self.dataclose[0] > self.bbands.top[0]
        trend_sig = self.lma[0] > self.lmama[0]
        risk_sig = self.datalow[0] <= self.stopprice


        if not self.position:
            if buy_sig:
                self.log(f"买入信号产生: 价格 {self.dataclose[0]:.2f} 跌破下轨 {self.lower_band[0]:.2f}")
                self.order = self.order_target_percent(target=self.p.target_pos)
        else:
            if not trend_sig:
                if sell_sig:
                    self.log(f"卖出信号产生: 价格 {self.dataclose[0]:.2f} 升穿上轨 {self.upper_band[0]:.2f}")
                    self.order = self.close()
                elif risk_sig:
                    loss_percent = 1 - (self.datalow[0] / self.buyprice)
                    self.log(f"ATR 止损信号产生: 当前最低价 {self.datalow[0]:.2f} 低于止损线 {self.stopprice:.2f}。已损失 {loss_percent:.2%}")
                    self.order = self.close()
