'''
实现策略并输出回测结果到 results 文件夹中
'''
import os.path
import sys

import datetime
import pandas as pd
import numpy as np
import backtrader as bt

if __name__ == "__main__":
    cerebro = bt.Cerebro()
    
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))

    print("Srarting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())