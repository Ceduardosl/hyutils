#%%
import pandas as pd
import numpy as np
from scipy import stats as st
import matplotlib.pyplot as plt
import statsmodels.api as sm
from glob import glob
#%% IDF
list_PMA = glob("PMA_basins/*.pkl")
path_PMA = list_PMA[0]
name = path_PMA.split("_")[-1].split(".")[0]

PMA = pd.read_pickle(path_PMA)
PMA_arr = PMA.to_numpy(dtype = "float64")


#%% Escolha da distribuição
dict_dist = {"gamma": st.gamma,
             "genextreme": st.genextreme,
             "norm": st.norm, 
             "lognorm": st.lognorm}

for i in dict_dist.keys():
    kms_test = st.kstest(PMA_arr, cdf = i, args = dict_dist[i].fit(PMA_arr))

    print(i)
    print("p-valor = {:.4f}".format(kms_test.pvalue))
    print("Estatística = {:.3f}".format(kms_test.statistic))
    print("\n")


for i in dict_dist.keys():
    fig, ax = plt.subplots()
    # st.probplot(PMA_arr, sparams = dict_dist[i], dist = i, plot = ax)
    # ax.set_title(" ", loc = "center")
    # ax.set_title(i, loc = "left")
    pp_pr = sm.ProbPlot(PMA_arr, dist = dict_dist[i], fit = True)
    qq_pr = pp_pr.qqplot(ax = ax, marker='o', markerfacecolor='k', markeredgecolor='k', alpha=0.3)
    sm.qqline(ax = ax, line='45', fmt='k--')
    ax.set_title(i)

#%%
trs = [5, 10, 15, 25, 50, 100, 1000, 10000]
args = st.gamma.fit(PMA_arr, floc = 0, method = "MM")
tr_df = pd.DataFrame([], columns = trs, index = [])

for i in tr_df.columns:
    tr_df.loc[name, i] = st.gamma.ppf(1 - (1/i), *args)

tr_df.to_pickle("Pr_Tr.pkl")

#%%
