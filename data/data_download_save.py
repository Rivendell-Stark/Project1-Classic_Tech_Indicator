'''
导入下载好的原始数据, 整理成格式化的数据并输出到Postgre数据库中。

原始数据：
    来源: CSMAR
    范围: 全部A股     
    时间: 2016-01-01 ~ 2025-11-10
    频率: 日度
    指标: 反正很多, 这里用到了OHLCVA数据(未复权)、涨跌停价格及涨跌停状态、当日交易状态, 以及累积前复权因子、累积后复权因子
'''

import pandas as pd
import numpy as np
import os
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine
from psycopg2.extras import execute_values

def read_csmar_excel(filepath):
    print(f"-> 正在读取文件:{os.path.basename(filepath)}")
    try:
        df = pd.read_excel(filepath, header=0, skiprows=[1,2])
        print(f"<- 读取文件成功 {filepath}")
        return df
    except Exception as e:
        print(f"<- 读取文件失败 {filepath}:{e}")
        return pd.DataFrame()
    
def raw_data_read():
        # 日度交易数据
    file_paths = []
    df_list = []

    for i in range(4):
        file = "D:\\Projects\\Quant\\1_CSMAR-Data\\A股-回报率\\日度交易数据16-20\\TRD_Dalyr%d.xlsx" % i
        file_paths.append(file)

    for i in range(7):
        file = "D:\\Projects\\Quant\\1_CSMAR-Data\\A股-回报率\\日度交易数据20-25\\TRD_Dalyr%d.xlsx" % i
        file_paths.append(file)
    
    with ProcessPoolExecutor(max_workers=11) as executor:
        future_to_file = {executor.submit(read_csmar_excel, file): file for file in file_paths}
        
        for future in concurrent.futures.as_completed(future_to_file):
            df = future.result()
            if not df.empty:
                df_list.append(df)

    raw = pd.concat(df_list, ignore_index=True)
    return raw

def fq_data_read():
    # 复权因子列表
    fq_file = r"D:\Projects\Quant\1_CSMAR-Data\A股-回报率\股票价格复权因子表(日)-A\TRD_AdjustFactor.xlsx"
    fq = read_csmar_excel(fq_file)
    fq.columns = "date code day_qfq day_hfq qfq hfq".split(" ")
    fq = fq.drop(columns="day_qfq day_hfq".split())
    return fq

def data_process(raw, fq):
    # 排序、列名更改
    raw = raw.sort_values(by=["Stkcd","Trddt"]).reset_index(drop=True)
    raw = raw[r"Stkcd	Trddt	Opnprc	Hiprc	Loprc	Clsprc	Dnshrtrd	Dnvaltrd	Dsmvosd	Dsmvtll	Markettype	Trdsta	LimitDown	LimitUp	LimitStatus".split("\t")]
    columns = r'code date open high low close volume amount float_value total_value market trade_status down_limit up_limit limit_status'.split(" ")
    raw.columns = columns

    # 合并列表，填充复权因子
    data = pd.merge(left=raw, right=fq, on=['code','date'], how="left")
    data[["qfq","hfq"]] = data.groupby("code")[["qfq","hfq"]].ffill()
    data[["qfq","hfq"]] = data[["qfq","hfq"]].fillna(1)
    
    # 数据类型转换
    data['code'] = data['code'].astype(str)
    data['date'] = pd.to_datetime(data["date"])
    data['volume'] = data["volume"].fillna(0).astype(np.int64)
    float_cols = "open high low close amount float_value total_value down_limit up_limit qfq hfq".split(" ")
    data[float_cols] = data[float_cols].astype(np.float64)
    int_cols = "market trade_status limit_status".split(" ")
    data[int_cols] = data[int_cols].fillna(-1).astype(np.int64)

    return data

def postgres_upsert(df: pd.DataFrame, table:str, engine:Engine):
    print(f"开始写入数据库...")
    
    columns = list(df.columns)
    columns_str = ', '.join([f'"{col}"' for col in columns])

    update_cols = [col for col in columns if col not in ['code', 'date']]
    update_set_str = ", ".join([f'"{col}" = EXCLUDED."{col}"' for col in update_cols])
    
    sql_template = f"""
    INSERT INTO "{table}" ({columns_str}) VALUES %s
    ON CONFLICT (code, date) DO UPDATE
    SET {update_set_str}
    """

    data_values = [tuple(row) for row in df.values]

    with engine.connect() as connection:
        conn = connection.connection
        with conn.cursor() as cursor:
            execute_values(
                cursor,
                sql_template,
                data_values,
                page_size=10000
            )
        conn.commit()
    print("数据写入完毕")


if __name__ == "__main__"   :

    # raw = raw_data_read()
    # raw.to_parquet("D:\\Projects\\Quant\\1_CSMAR-Data\\A股-回报率\\raw.parquet")
    # raw = pd.read_parquet(r"D:\Projects\Quant\1_CSMAR-Data\A股-回报率\raw.parquet")

    # # fq = fq_data_read()
    # # fq.to_parquet(r"D:\Projects\Quant\1_CSMAR-Data\A股-回报率\fq_clean.parquet")
    # fq = pd.read_parquet(r"D:\Projects\Quant\1_CSMAR-Data\A股-回报率\fq_clean.parquet")

    # data = data_process(raw, fq)
    # data.to_parquet(r"D:\Projects\Quant\1_CSMAR-Data\A股-回报率\data_clean.parquet")    
    # data = pd.read_parquet(r"D:\Projects\Quant\1_CSMAR-Data\A股-回报率\data_clean.parquet")



    # 存入数据库
    db_url = f"postgresql+psycopg2://maxkirby:123456@localhost:5432/stock_db"
    engine = create_engine(db_url)

    table_name = 'daily_price'
    postgres_upsert(data, table_name, engine)
