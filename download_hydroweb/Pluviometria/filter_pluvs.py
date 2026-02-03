#%%
import pandas as pd
from glob import glob
import numpy as np
#%%

path_pluvs = glob("raw_pluvs/*.csv")

#%%

df = pd.DataFrame([], columns = [], index = pd.date_range("01-01-1900", "12-31-2024", freq = "D"))


for path in path_pluvs:

    pluv_id = path.split("_")[-1].split(".")[0]
    pluv_data = pd.read_csv(path, sep = ";", index_col = 0)
    pluv_data.index = pd.to_datetime(pluv_data.index)
    
    cons_data = pluv_data["pr"].loc[pluv_data["Consistency"] == 2]

    cons_data = cons_data.drop_duplicates()
    raw_data = pluv_data["pr"].loc[pluv_data["Consistency"] == 1]
    raw_data = raw_data.groupby(raw_data.index).max()

    df[pluv_id] = np.nan
    df[pluv_id] = df[pluv_id].fillna(cons_data)
    df[pluv_id] = df[pluv_id].fillna(raw_data)

#%%
df_nonan = df.dropna(axis = 0, how = 'all')
df_nonan = df_nonan.dropna(axis = 1, how = 'all')
df_nonan.to_pickle("filtered_pluvs.pkl")
#%%
df_count = df_nonan.groupby([df_nonan.index.year, df_nonan.index.month]).count()
df_count.reset_index(drop = False, inplace = True)
df_count.rename(columns = {"level_0": "Ano", "level_1": "Mês"}, inplace = True)
df_count = df_count.loc[df_count["Mês"] <= 5]
#%%
df_count.to_excel("count_data.xlsx", sheet_name = "filtered_pluvs")
#%%