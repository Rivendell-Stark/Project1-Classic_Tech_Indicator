import backtrader as bt

class TestStrategy(bt.Strategy):
    """一个简单的占位策略，用于验证数据加载和Cerebro运行。"""
    
    # 打印出每个数据源的名称和最新价格
    def next(self):
        for i, data in enumerate(self.datas):
            dt = self.datetime.date()
            if data.datetime[0] > 0:
                print(f'{dt} | {data._name} - Close: {data.close[0]:.2f}')