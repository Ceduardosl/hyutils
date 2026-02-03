#%%

import pandas as pd
import pyHidroWeb

#%%
df_pluv = pd.read_excel("pluvs_ANA.xlsx")

list_pluvs = list(df_pluv["Codigo"].values)

for pluv in list_pluvs:

    data = pyHidroWeb.download_hidroweb_data(pluv, data_type = 2, output_format = 0)
    data = data.rename(columns = {data.columns[0]: "Consistency", data.columns[1]: "pr"})
    data.to_csv("raw_pluvs/pluv_{}.csv".format(pluv), index = True, header = True, sep = ";")
#%%

