"""
用于从数据库中查询需要的股票数据

"""
import pandas as pd
from sqlalchemy import create_engine

def read_db(stock_list, start_date, end_date, table_name='daily_price', db_url="postgresql+psycopg2://maxkirby:123456@localhost:5432/stock_db"):
    
    
    pass



db_url = f"postgresql+psycopg2://maxkirby:123456@localhost:5432/stock_db"
engine = create_engine(db_url)

table_name = 'daily_price'


