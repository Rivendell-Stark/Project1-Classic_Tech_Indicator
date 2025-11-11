'''
用于爬取股票数据, 存储到数据库中。

股票范围: 
股票时间: 

说明: 价格为未复权价格
'''

import numpy as np
import pandas as pd
import psycopg2 as pg

kc1 = pd.read_excel(r"D:/Projects/Quant/CSMAR-Data/科创16-20.xlsx", header=0, skiprows=[1,2])
kc2 = pd.read_excel(r"D:/Projects/Quant/CSMAR-Data/科创20-25.xlsx", header=0, skiprows=[1,2])
kc = pd.concat([kc1,kc2], ignore_index= True, copy=False).sort_values(by=["Stkcd","Trddt"])

fq1 = pd.read_excel(r"D:/Projects/Quant/CSMAR-Data/TRD_AdjustFactor.xlsx", header=0, skiprows=[1,2]).drop(columns=["CumulateFwardFactor","FwardFactor"])
fq2 = fq1.head(0)
fq2[["Stkcd","Trddt"]] = kc.groupby('Stkcd')['Trddt'].min().reset_index()
fq2 = fq2.fillna(1)
fq = pd.concat([fq1,fq2], ignore_index= True, copy=False).sort_values(by=["Stkcd","Trddt"])

kc_merged = pd.merge(left=kc, right=fq, how='left', on=["Trddt",'Stkcd'], copy=False)
kc_merged[["BwardFactor","CumulateBwardFactor"]] = kc_merged.groupby("Stkcd")[["BwardFactor","CumulateBwardFactor"]].fillna(method='ffill')


saved_list = ["CumulateBwardFactor","Stkcd","Trddt","Opnprc","Hiprc","Loprc","Clsprc","Dretwd","Dretnd","Dnshrtrd","Dnvaltrd","Markettype","Dsmvosd","Trdsta","Dsmvtll"]
