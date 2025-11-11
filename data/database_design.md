数据库结构设计

| daily_price | 类型            | 约束           | 说明       |
| ----------- | --------------- | ------------- | ---------- | 
| code        | char(6)         | 联合主键       | 股票代码 |
| date        | char(10)        | 联合主键       | 交易日期   |
| open        | numeric(9, 3)   | 非空           | 开盘价     |
| high        | numeric(9, 3)   | 非空           | 最高价     |
| low         | numeric(9, 3)   | 非空           | 最低价     |
| close       | numeric(9, 3)   | 非空           | 收盘价     |
| volume      | numeric(12, 0)  | 非空           | 交易量     |
| amount      | numeric(16, 3)  | 非空           | 交易价值   |
| adj_factor  | numeric(12, 6)  | 非空           | 复权因子   |

```{SQL}
create table daily_price(
    code char(6) NOT NULL,
    date char(10) NOT NULL,
    open numeric(9,3) not null,
    high numeric(9,3) not null,
    low numeric(9,3) not null,
    close numeric(9,3) not null,
    volume numeric(12,0) not null,
    amount numeric(16,3) not null,
    adj_factor numeric(12,6) not null,
    primary key (code, date)
);
```