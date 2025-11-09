数据库结构设计

### 表1：股票代码表，可拓展股票名字、行业、交易所、板块、是否停牌、是否ST

| stock | 类型        | 约束       | 说明     |
|-------|-----------|------------|----------|
| id    | primary key | 主键       | 自增主键 |
| code  | varchar(20) | 非空，唯一 | 股票代码 |

```{SQL}
create table stock(
    id serial primary key,
    code varchar(20) not null unique
);
```

```{plain text}
stock_db=> \d stock
                                  数据表 "public.stock"
 栏位 |         类型          | 校对规则 |  可空的  |                预设
------+-----------------------+----------+----------+------------------------------------
 id   | integer               |          | not null | nextval('stocks_id_seq'::regclass)
 code | character varying(20) |          | not null |
索引：
    "stocks_pkey" PRIMARY KEY, btree (id)
    "stocks_code_key" UNIQUE CONSTRAINT, btree (code)
由引用：
    TABLE "daily_price" CONSTRAINT "daily_price_stock_id_fkey" FOREIGN KEY (stock_id) REFERENCES stock(id)


stock_db=>
```

### 表2：日度交易表

| daily_price | 类型           | 约束           | 说明       |
| ----------- | -------------- | ------------- | ---------- | 
| stock_id    | integer        | 外键，联合主键  | 股票代码id |
| date        | date           | 联合主键       | 交易日期   |
| open        | numeric(18, 4) | 非空           | 开盘价     |
| high        | numeric(18, 4) | 非空           | 最高价     |
| low         | numeric(18, 4) | 非空           | 最低价     |
| close       | numeric(18, 4) | 非空           | 收盘价     |
| volume      | bigint         | 非空           | 交易量     |
| amount      | numeric(20,2)  | 非空           | 交易价值   |
| adj_factor  | numeric(18,6)  | 非空           | 复权因子   |


```{SQL}
create table daily_price(
    stock_id integer references stock(id) NOT NULL,
    date date NOT NULL,
    open numeric(18,4) not null,
    high numeric(18,4) not null,
    low numeric(18,4) not null,
    close numeric(18,4) not null,
    volume bigint not null,
    amount numeric(20,2) not null,
    adj_factor numeric(18,6) not null,
    primary key (stock_id, date)
);
```

```{plain text}
stock_db=> \d daily_price
               数据表 "public.daily_price"
    栏位    |     类型      | 校对规则 |  可空的  | 预设
------------+---------------+----------+----------+------
 stock_id   | integer       |          | not null |
 date       | date          |          | not null |
 open       | numeric(18,4) |          | not null |
 high       | numeric(18,4) |          | not null |
 low        | numeric(18,4) |          | not null |
 close      | numeric(18,4) |          | not null |
 volume     | bigint        |          | not null |
 amount     | numeric(20,2) |          | not null |
 adj_factor | numeric(18,6) |          | not null |
索引：
    "daily_price_pkey" PRIMARY KEY, btree (stock_id, date)
外部键(FK)限制：
    "daily_price_stock_id_fkey" FOREIGN KEY (stock_id) REFERENCES stock(id)


stock_db=> 
```