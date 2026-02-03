#%%
import pandas as pd
import numpy as np
from scipy import stats as st
import matplotlib.pyplot as plt
from glob import glob
#%%
def get_pr_values(t, P6m, P1h, P24h):
    
    P1 = P6m #6minutos
    P2 =  P1h #1 hora = 60 minutos
    P3 =  P24h #24 horas = 1440 minutos

    t1 = 6
    t2 = 60
    t3 = 1440

    if t in [6, 60, 1440]:
        if t == 6:
            y = P1
        if t == 60:
            y = P2
        if t == 1440:
            y = P3

    if t not in [6, 60, 1440]:

        if t == 0:
            y = 0

        if (t <= 1440) & (t >= 6): #Tem que ser no mínimo 6 minutos

            if (t > 6) & (t < 60):
                x1 = t1
                x2 = t2
                y1 = P1
                y2 = P2

            if (t > 60) & (t < 1440):
                x1 = t2
                x2 = t3
                y1 = P2
                y2 = P3

            y = y1 + ((np.log(t) - np.log(x1))/(np.log(x2) - np.log(x1))) * (y2 - y1)

        if t > 1440:

            x_reg = [np.log(t2), np.log(t3)]
            y_reg = [P2, P3]

            coef = np.polyfit(x_reg, y_reg, 1)

            y = coef[0]*np.log(t) + coef[1]
   
    return y

def Taborga(tr_df, isozona, coef_Taborga_24h, tc, d):
    
    Taborga_1_24 = pd.read_pickle("Taborga_Coef_1h_24h.pkl")
    Taborga_6_24 = pd.read_pickle("Taborga_Coef_6min_24h.pkl")

    trs = tr_df.index

    P24h_tr = tr_df * coef_Taborga_24h
    P1h_tr = P24h_tr * Taborga_1_24.loc[isozona, trs]
    P6m_tr = P24h_tr * Taborga_6_24.loc[isozona, trs]

    tc = (tc + d) - ((tc + d) % d) 

    prj_rain = pd.DataFrame([], index = np.arange(d, tc + d, d))
    
    for tr in trs:
        P6m = P6m_tr[tr]
        P1h = P1h_tr[tr]
        P24h = P24h_tr[tr]

        for t in prj_rain.index:
            prj_rain.loc[t, tr] = get_pr_values(t, P6m, P1h, P24h)
    
    return prj_rain

def Hyetograph(prj_rain):

    inc_pr = prj_rain.diff()
    inc_pr.iloc[0,:] = prj_rain.iloc[0,:]
    hiet_proj = pd.DataFrame([], index = inc_pr.index, columns = inc_pr.columns)
    n_blocks = inc_pr.shape[0]
    for i in inc_pr.columns:
        n = inc_pr.shape[0]
        aux = inc_pr[i].sort_values(ascending=False).to_numpy()
        aux_right = [x for index, x in enumerate(aux) if ((index % 2) == 0)]
        aux_left = [x for index, x in enumerate(aux) if ((index % 2) != 0)]
        aux_left.sort()
        order_inc = np.empty(shape = (n_blocks))

        if aux.shape[0] % 2 == 0:
            s_idx = n_blocks/2
            order_inc[int(s_idx):] = aux_right
            order_inc[0:int(s_idx)] = aux_left
        else:
            s_idx = (((n_blocks + 2) - ((n_blocks + 2) % 2))/2) - 1 #Econtrar o múltiplo de 2 mais próximo e subtrai 1
            order_inc[int(s_idx):] = aux_right
            order_inc[0:int(s_idx)] = aux_left
    
        hiet_proj[i] = order_inc

    return hiet_proj
#%%

tc = 1440 #duração total
d = 6
isozona = "D"

Taborga_1_24 = pd.read_pickle("Taborga_Coef_1h_24h.pkl")
Taborga_6_24 = pd.read_pickle("Taborga_Coef_6min_24h.pkl")

tr_df = pd.read_pickle("Pr_Tr/Pr_Tr.pkl")
trs = tr_df.columns

P24h_tr = tr_df * 1.1
P1h_tr = P24h_tr[trs].mul(Taborga_1_24.loc[isozona, trs], axis = 1)
P6m_tr = P24h_tr[trs].mul(Taborga_6_24.loc[isozona, trs], axis = 1)
#%%
for model in tr_df.index:
    prj_rain = pd.DataFrame([], index = np.concat(
        [np.arange(6, 60 + 6, 6), np.arange(90, 1440 + 30, 30)])
        )
    for tr in trs:
        P6m = P6m_tr.loc[model, tr]
        P1h = P1h_tr.loc[model, tr]
        P24h = P24h_tr.loc[model, tr]
        for t in prj_rain.index:
            prj_rain.loc[t, tr] = get_pr_values(t, P6m, P1h, P24h)
    prj_rain.index.name = "duracao"
    prj_rain.to_csv("prj_rain/prj_rain_obs.csv")
#%%
#         prj_hyetograph = Hyetograph(prj_rain)
#         prj_hyetograph.index.name = "duracao"
#         # prj_hyetograph.to_pickle("hyetographs/{}_{}.pkl".format(model, sc))
#         # prj_hyetograph.to_csv("hyetographs/{}_{}.csv".format(model, sc))
# #%%

# inc_pr = prj_rain.diff()
# inc_pr.iloc[0,:] = prj_rain.iloc[0,:]
# hiet_proj = pd.DataFrame([], index = inc_pr.index, columns = inc_pr.columns)
# n_blocks = inc_pr.shape[0]
# for i in inc_pr.columns:
#     n = inc_pr.shape[0]
#     aux = inc_pr[i].sort_values(ascending=False).to_numpy()
#     aux_right = [x for index, x in enumerate(aux) if ((index % 2) == 0)]
#     aux_left = [x for index, x in enumerate(aux) if ((index % 2) != 0)]
#     aux_left.sort()
#     order_inc = np.empty(shape = (n_blocks))

#     if aux.shape[0] % 2 == 0:
#         s_idx = n_blocks/2
#         order_inc[int(s_idx):] = aux_right
#         order_inc[0:int(s_idx)] = aux_left
#     else:
#         s_idx = (((n_blocks + 2) - ((n_blocks + 2) % 2))/2) - 1 #Econtrar o múltiplo de 2 mais próximo e subtrai 1
#         order_inc[int(s_idx):] = aux_right
#         order_inc[0:int(s_idx)] = aux_left

#     hiet_proj[i] = order_inc

# cum_hiet = hiet_proj.cumsum()
#%%