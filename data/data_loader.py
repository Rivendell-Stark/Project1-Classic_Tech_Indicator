"""
用于从数据库中查询需要的股票数据, 返回df_list为数据源

"""
import pandas as pd
from sqlalchemy import create_engine, Engine
from typing import List, Dict

DB_URL = f"postgresql+psycopg2://maxkirby:123456@localhost:5432/stock_db"

def get_db_engine() -> Engine:
    return create_engine(DB_URL)


def load_single_stock_data(
        code: str,
        start_date: str,
        end_date: str,
        fq : str = "hfq",
        engine: Engine = None
        ) -> pd.DataFrame:

    if engine is None:
        engine = get_db_engine()

    fq = fq.lower()

    if fq not in ['qfq', 'hfq']:
        raise ValueError("fq 参数必须是 'qfq' 或 'hfq'")

    print(f"-> 正在加载{code}数据, 复权方式为{fq}...")

    sql_query = f"""
    SELECT
        date, open, high, low, close, volume, {fq}
    FROM daily_price
    WHERE
        code = '{code}'
        AND date BETWEEN '{start_date}' and '{end_date}'
        AND trade_status = 1
    ORDER BY date ASC;
    """
    
    try:
        df = pd.read_sql(sql_query, engine, index_col='date', parse_dates=['date'])
    except Exception as e:
        print(f"错误：股票 {code} 数据加载失败：{e}")
        return pd.DataFrame()
    
    if df.empty:
        return pd.DataFrame()

    df['open'] = df['open'] * df[fq]
    df['high'] = df['high'] * df[fq]
    df['low'] = df['low'] * df[fq]
    df['close'] = df['close'] * df[fq]

    return df['open high low close volume'.split()]

def load_stock_data(
    stock_list: List[str],
    start_date: str,
    end_date: str,
    fq: str = "hfq"
) -> Dict[str, pd.DataFrame]:
    """
    加载多只股票数据，并返回一个字典 {code: DataFrame}。
    """

    engine = get_db_engine()
    data_dict = {}
    
    for code in stock_list:
        df = load_single_stock_data(code, start_date, end_date, fq, engine=engine)
        if not df.empty:
            data_dict[code] = df
            
    return data_dict

