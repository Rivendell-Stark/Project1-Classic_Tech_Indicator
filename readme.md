借助Backtrader实现的一个回测框架。我使用的是学校购买的CSMAR的数据，所以项目本身不包含数据。  

  
- data/ : 数据处理部分  
  - data_download_save.py : 将下载好的CSMAR数据整理到一起，处理后导入本地数据库中  
  - data_loader : 从数据库中将股票数据导出到回测主文件中，作为数据源  
- strategies/ : 策略实现部分  
  - _Base_Strategy.py : 一个基础策略，作用是内置日志记录功能，作为基类被继承时可以在结果文件夹里生成一个日志文件，记录系统的交易记录  
  - _Test_Strategy.py : 一个测试策略和一个买入并持有策略，作用是检查回测框架本身是否有问题  
  - DMA_strategy.py : 一个简单的双均线策略，金叉时买入，死叉时卖出  
  - RSI_strategy.py : 主要使用RSI的策略，包括一个反转策略（RSI反映超买超卖）和一个趋势策略（RSI确认上涨/下跌趋势）。相比于双均线策略，采用ATR作为止损指标，并加入了趋势过滤指标进行优化。
- utils/ : 功能性函数
  - main.py : 回测时常用的一些函数，包括生成结果文件夹并记录回测日志的函数、生成文件名的函数、同时在控制台和日志中输出的函数
  - analysis.py : 分析回测结果的函数，包括提取analyzer结果的函数和利用PyFolio的收益率序列生成quantstats报告的函数
  - visualization.py : 回测结果可视化的函数，目前只有根据二维的优化结果生成热力图的函数
- backtest.py: 回测主函数与参数优化函数
- Strategy_Configs.py: 保存所有策略的参数格式设置
  
----------------------------  



-----------------------------

python version: 3.13.9

libraries: numpy、pandas 、matplotlib 、seaborn 、backtrader 、quantstats 、pyfolio 、sqlalchemy 、psycopg2


数据库表结构： 

tablename: 'daily_price'

|     栏位      |     类型      | 校对规则  |  可空的  | 预设  |   存储   | 压缩 | 统计目标  | 描述   |
| ------------ | ------------- | -------- | -------- | ---- | -------- | ---- | -------- | ------ |
| code         | character(6)  |          | not null |      | extended |      |          |        |
| date         | date          |          | not null |      | plain    |      |          |        |
| open         | numeric(9,3)  |          | not null |      | main     |      |          |        |
| high         | numeric(9,3)  |          | not null |      | main     |      |          |        |
| low          | numeric(9,3)  |          | not null |      | main     |      |          |        |
| close        | numeric(9,3)  |          | not null |      | main     |      |          |        |
| volume       | bigint        |          | not null |      | plain    |      |          |        |
| amount       | numeric(16,3) |          | not null |      | main     |      |          |        |
| hfq          | numeric(12,6) |          | not null |      | main     |      |          |        |
| qfq          | numeric(12,6) |          | not null |      | main     |      |          |        |
| trade_status | smallint      |          | not null |      | plain    |      |          |        |
| limit_status | smallint      |          |          |      | plain    |      |          |        |
| up_limit     | numeric(10,3) |          |          |      | main     |      |          |        |
| down_limit   | numeric(10,3) |          |          |      | main     |      |          |        |
| float_value  | numeric(16,2) |          | not null |      | main     |      |          |        |
| total_value  | numeric(16,2) |          | not null |      | main     |      |          |        |
| market       | smallint      |          | not null |      | plain    |      |          |        |

索引：
  - "daily_price_pkey" PRIMARY KEY, btree (code, date)

检查约束限制
  - "factor_positive_check" CHECK (qfq > 0::numeric AND hfq > 0::numeric)
  - "ohlc_range_check" CHECK (high >= open AND high >= close AND low <= open AND low <= close AND high >= low)
  - "price_integrity_check" CHECK (open >= 0::numeric AND high >= 0::numeric AND low >= 0::numeric AND close >= 0::numeric)
  - "volume_amount_check" CHECK (volume >= 0 AND amount >= 0::numeric)

Not-null constraints:
  - "daily_price_code_not_null" NOT NULL "code"
  - "daily_price_date_not_null" NOT NULL "date"
  - "daily_price_open_not_null" NOT NULL "open"
  - "daily_price_high_not_null" NOT NULL "high"
  - "daily_price_low_not_null" NOT NULL "low"
  - "daily_price_close_not_null" NOT NULL "close"
  - "daily_price_volume_not_null" NOT NULL "volume"
  - "daily_price_amount_not_null" NOT NULL "amount"
  - "daily_price_adj_factor_not_null" NOT NULL "hfq"
  - "daily_price_qfq_not_null" NOT NULL "qfq"
  - "daily_price_trade_status_not_null" NOT NULL "trade_status"
  - "daily_price_float_value_not_null" NOT NULL "float_value"
  - "daily_price_total_value_not_null" NOT NULL "total_value"
  - "daily_price_market_not_null" NOT NULL "market"
