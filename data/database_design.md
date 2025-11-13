
 |     栏位      |     类型      | 校对规则 |  可空的  | 预设 |   存储   | 压缩 | 统计目标 | 描述 |
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
