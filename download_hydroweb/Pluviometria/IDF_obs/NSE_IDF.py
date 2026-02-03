#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.ioff()
#%%
def IDF (params, tr, t):
    a = params[0]
    b = params[1]
    c = params[2]
    d = params[3]
    
    return (a * np.power(tr, b))/np.power(t + c, d)

def NSE_calc(params, df_obs):
    params = tuple(params)
    df_NSE = df_obs.copy()
    df_NSE["i_mod"] = IDF(params, df_NSE["tr"], df_NSE["t"])
    df_NSE["num"] = np.power(df_NSE["i"] - df_NSE["i_mod"], 2)
    df_NSE["den"] = np.power(df_NSE["i"] - df_NSE["i"].mean(), 2)

    return (1 - ((df_NSE["num"].sum()) / (df_NSE["den"].sum())))
#%%
params_obs = (1070.023, 0.0818, 9.791, 0.7244)

coef_IDF = pd.read_csv("Coef_IDF.csv")
coef_IDF = coef_IDF[["name", "a", "b", "c", "d"]]
output = coef_IDF.copy()
output["NSE"] = np.nan
for i in coef_IDF.index:
    sel_IDF = coef_IDF.loc[i, :]
    model = sel_IDF["name"].split("_")[0]
    if "ssp245" in sel_IDF["name"]:
        sc = "SSP2-4.5"
    if "ssp585" in sel_IDF["name"]:
        sc = "SSP5-8.5"

    obs_df = pd.read_csv("prj_rain/{}.csv".format(sel_IDF["name"]), index_col = 0)
    obs_df.columns = obs_df.columns.astype(int)
    df_melt = obs_df.melt(ignore_index = False).reset_index(drop = False)
    df_melt = df_melt.rename(columns = {
        df_melt.columns[0]:"t",
        df_melt.columns[1]:"tr",
        df_melt.columns[2]: "i"
    })
    df_melt["i"] = df_melt["i"]/(df_melt["t"]/60)


    output.loc[i, "NSE"] = NSE_calc(params = tuple(sel_IDF.iloc[1:]), df_obs = df_melt)

output.to_csv("Coef_IDF_NSE.csv", sep = ";", index = None, header = True)
#%%
params = sel_IDF[1:]
df_plot = pd.DataFrame(index = df_melt["t"].unique())

for tr in [5, 10, 25, 50, 100, 1000, 10000]:
    df_plot[tr] = IDF(params = tuple(sel_IDF.iloc[1:]), tr = tr, t = df_plot.index)
    df_plot[tr] = df_plot[tr] * (df_plot.index/60)

#%%
fig, ax = plt.subplots(dpi = 600)
for i in df_plot.columns:

    if i == 1000:
        label = "Tr = 1.000 anos"
    elif i == 10000:
        label = "Tr = 10.000 anos"
    else:
        label = "Tr = {} anos".format(i)
    ax.plot(df_plot[i], label = label)
    ax.legend(ncols = 2)
    ax.set_ylabel("Precipitação (mm)")
    ax.set_xlabel("Duração (min)")
    fig.savefig("figs_IDF/IDF_obs.png", dpi = 600, bbox_inches = "tight", facecolor = 'w')
#%%

