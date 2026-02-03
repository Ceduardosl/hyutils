#%%
import numpy as np
import matplotlib.pyplot as plt
import smapm
from pyswarms.single.global_best import GlobalBestPSO
import pandas as pd

#%%

params_df = pd.read_csv("opt_coef_5305.csv", index_col = 0)

opt_params = params_df.to_numpy().flatten()

#%%

Cap1_df = pd.read_excel("input_data_Captacoes.xlsx", sheet_name = "Ribeirao", index_col = 0)
Cap2_df = pd.read_excel("input_data_Captacoes.xlsx", sheet_name = "FMoura", index_col = 0)
Cap3_df = pd.read_excel("input_data_Captacoes.xlsx", sheet_name = "FSHelena", index_col = 0)

area_cap1 = 0.32
area_cap2 = 0.20
area_cap3 = 0.33

#%%
Cap1_sim = smapm.smapm(opt_params, area = area_cap1,
                       prec = Cap1_df.P.to_numpy(),
                       pet = Cap1_df.ETP.to_numpy())
Cap2_sim = smapm.smapm(opt_params, area = area_cap2,
                       prec = Cap2_df.P.to_numpy(),
                       pet = Cap2_df.ETP.to_numpy())
Cap3_sim = smapm.smapm(opt_params, area = area_cap3,
                       prec = Cap3_df.P.to_numpy(),
                       pet = Cap3_df.ETP.to_numpy())

#%%
warm = 12
sim_df = pd.DataFrame({
    "Ribeirao": Cap1_sim[warm:],
    "Faz_Moura": Cap2_sim[warm:],
    "Faz_SHelena": Cap3_sim[warm:]
}, index = Cap1_df.index[warm:])

sim_df.to_csv("sim_streamflow/Vazoes_Regionalizadas_Captacoes.csv", index = True, header = True)


#%%

for col in sim_df.columns:
    mon_x = sim_df[col].to_numpy()

    perm_list = []

    for p in range(1, 100, 1):
        if (p == 1) | (p == 99) | (p%5 == 0):
            perm_list.append([p/100, 1-(p/100), np.quantile(mon_x, p/100)])

    perm_df = pd.DataFrame(perm_list, columns = ["Quantile", "Permanence", "mon_streamflow"])
    perm_df.to_csv("sim_streamflow/Permanencia/{}.csv".format(col), index = None, header = True)