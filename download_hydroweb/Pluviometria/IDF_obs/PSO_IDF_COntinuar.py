#%%
import pyswarms as psw
import pandas as pd
import numpy as np
from glob import glob

def IDF(params, tr, t):
    a = params[0]
    b = params[1]
    c = params[2]
    d = params[3]

    return (a * np.power(tr, b))/np.power(t+c, d)


def FO(params, tr, t, obs_df):
    df = obs_df.copy()
    df["mod"] = df.apply(lambda x: IDF(params, tr, df.index.values), axis = 1)

#%%
list_files = glob("hyetographs/*.csv")
path = [x for x in list_files if "MRI-ESM2-0_ssp585" in x][0]

prj_hyet = pd.read_csv(path, index_col = 0)
prj_hyet.columns = prj_hyet.columns.astype(int)
prj_hyet = prj_hyet.cumsum()
hyet_melt = prj_hyet.melt(ignore_index = False).reset_index(drop = False)
hyet_melt = hyet_melt.rename(columns = {
    hyet_melt.columns[0]:"t",
    hyet_melt.columns[1]:"tr",
    hyet_melt.columns[2]: "i"
})
hyet_melt["i"] = hyet_melt["i"]/(hyet_melt["t"]/60)
hyet_melt = hyet_melt.sort_values(by = "t", ascending = True)
# hyet_melt = hyet_melt.reset_index(drop = False)

#%%
inital_guess = (0,0,0,0)
bounds = (2000, 1, 20, 1)
n_particles = 100
options = {
    'c1': 0.5,  # cognitive parameter
    'c2': 0.3,  # social parameter
    'w': 0.9   # inertia weight
}