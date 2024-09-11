import os
import pandas as pd

datas = [data for data in os.listdir('data/raw') if data.endswith('.csv')]

for data in datas: 
    data = os.path.join('data/raw', data)
    df = pd.read_csv(data)
    print(df.columns)
    