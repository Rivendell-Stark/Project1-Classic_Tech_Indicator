'''
用于爬取股票数据, 存储到数据库中。

股票范围: 沪深300成分股
股票时间: 2020.1.1 ~ 2025.11.10

说明: 价格为未复权价格
'''

import numpy
import pandas
import akshare
import psycopg2


