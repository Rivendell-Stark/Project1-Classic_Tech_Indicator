'''
实现策略并输出回测结果到 results 文件夹中
'''
from __future__ import (absolute_import, division, print_function, unicode_literals)  
import os.path
import sys

import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds

