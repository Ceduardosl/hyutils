#%%
#Faz correção de falhas de todas as séries com regressão múltipla
#Aplica Thiessen (Precisar informar as áreas de cada estação)
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
#%%
df_raw = pd.read_pickle("filtered_pluvs.pkl")
df_raw.index = pd.to_datetime(df_raw.index)
#%%
id_pluvs = ["440007", "440014", "539021", "540003", "540020", "640002"]
df_sel = df_raw.loc[:, id_pluvs]

df_sel = df_sel.loc[df_sel.index.year >= 1911]

df_count = df_sel.loc[df_sel.index.month <= 5].isna().sum()

#%%
month_na = df_sel.groupby([df_sel.index.year, df_sel.index.month]).count()
month_na.reset_index(drop = False, inplace = True)
month_na.rename(columns = {"level_0": "year", "level_1": "month"}, inplace = True)

#%%
PMA_df = pd.DataFrame([], index = range(df_sel.index.year[0], df_sel.index.year[-1] + 1, 1), columns = df_sel.columns)

for pluv in PMA_df.columns:
    for year in PMA_df.index:
        ts_year = df_sel.loc[df_sel.index.year == year, pluv]
        count_na = ts_year.loc[ts_year.index.month <= 5]
        count_na = count_na.groupby(count_na.index.month).count()
        if 25 not in count_na.to_list():
            PMA = ts_year.max()
            if PMA != 0:
                PMA_df.loc[year, pluv] = PMA


PMA_nonan = PMA_df.dropna()
for pluv in PMA_df.columns:

    idx_na = PMA_df.loc[PMA_df[pluv].isnull()]
    y = PMA_nonan[pluv].to_numpy(dtype = "float64")
    for idx in idx_na.index:
        X_pluvs = idx_na.loc[idx].dropna().index.to_list()
        X = np.empty(shape = (PMA_nonan.shape[0], len(X_pluvs) + 1))

        X[:, 0] = np.ones(shape = (X.shape[0]))

        for i, j in zip(range(1, X.shape[1]), X_pluvs):
            X[:, i] = PMA_nonan[j].to_numpy()
    
        if X.shape[0] != X.shape[1]:
            coef_matrix = np.linalg.lstsq(X,y)[0]
        else:
            coef_matrix = np.linalg.solve(X,y)[0]

        X_pred = np.append(np.ones(1), idx_na.loc[idx].dropna().to_numpy())
        y_pred = np.dot(coef_matrix, X_pred)
        PMA_df.loc[idx, pluv] = y_pred
# %%

thiessen_areas = {
    "640002": 473.329059,
    "539021": 1561.958486,
    "540020": 2978.569996,
    "540003": 3181.448484,
    "440007": 1469.106629,
    "440014": 614.7696
}

thiessen_df = pd.DataFrame([], columns = PMA_df.columns)

for i in PMA_df.columns:
    thiessen_df[i] = PMA_df[i] * thiessen_areas[i]

avg_PMA = thiessen_df.sum(axis = 1) / sum(thiessen_areas.values())
avg_PMA.to_pickle("avg_PMA.pkl")
#%%