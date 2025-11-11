'''
原始数据：
    范围: 全A股     
    时间: 2021-11-11 ~ 2025-11-10 

筛选：
    范围: 沪深300成分股
    时间: 2021-11-11 ~ 2025-11-10 

复权方式: 后复权
'''
import pandas as pd


def hs300_idx_process(df_raw):
    columns = ['index', "date", "open", 'high', 'low', 'close', 'volume', 'amount', 'return']
    df_raw.columns = columns
    
    df = df_raw.drop(columns=["index","amount","return"])
    
    df["date"] = pd.to_datetime(df['date'])
    df = df[df["date"] >= pd.to_datetime("2022-01-01")]
    
    df = df.reset_index()
    
    df.to_csv(r"D:\Projects\Quant\Project1-Classic_Tech_Indicator\data\hs300-22-25.csv", index=False, sep=",")

if __name__ == "__main__":

    hs300_raw = pd.read_excel(r"D:\Projects\Quant\CSMAR-Data\沪深300\国内指数日行情文件142909002(仅供复旦大学使用)\hs300-211111-251110.xlsx",header=0, skiprows=[1,2])

    hs300_idx_process(hs300_raw)