#%%
import pandas as pd
import numpy as np
from scipy import stats as st
import matplotlib.pyplot as plt
import statsmodels.api as sm
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
    isozona = "D"

    P24h_tr = tr_df * coef_Taborga_24h
    P1h_tr = P24h_tr * Taborga_1_24.loc[isozona, trs]
    P6m_tr = P24h_tr * Taborga_6_24.loc[isozona, trs]
    d = 30
    tc = (tc + d) - ((tc + d) % d) 

    project_rain = pd.DataFrame([], index = np.arange(d, tc + d, d))
    
    for tr in trs:
        P6m = P6m_tr[tr]
        P1h = P1h_tr[tr]
        P24h = P24h_tr[tr]

        for t in project_rain.index:
            project_rain.loc[t, tr] = get_pr_values(t, P6m, P1h, P24h)
    
    return project_rain

def Hyetograph(project_rain):
    #Blocos Alternados
    inc_pr = project_rain.diff()
    inc_pr.iloc[0,:] = project_rain.iloc[0,:]
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

def prj_rain_IDF(a, b, c, d, du, inc_du, trs):
    #du = duração chuva (min)
    #inc_du = incremento de tempo (min)
    #a,b,c,d = parâmetros IDF
    #trs = períodos de retorno
    project_rain = pd.DataFrame(index = range(inc_du, du + inc_du, inc_du))
    for tr in trs:

        project_rain[tr] = (a*np.power(tr, b)) / np.power(project_rain.index + c, d)
        project_rain[tr] = project_rain[tr]*(project_rain.index/60)

    return project_rain
#%%

if __name__ == "__main__":
    
    a = 1602.955
    b = 0.110
    c = 19.334
    d = 0.773

    du = 10
    td = 180

    project_rain = pd.DataFrame(index = range(du, td + du, du))

    for tr in [25, 50, 100, 1000]:


        project_rain[tr] = (a*np.power(tr, b)) / np.power(project_rain.index + c, d)
        project_rain[tr] = project_rain[tr]*(project_rain.index/60)

    test = prj_rain_IDF(a,b,c,d,td,du,[25, 50, 100, 1000])

    hyet = Hyetograph(project_rain)
    hyet.plot.bar()
    #%%
    tc = 2354.247554
    d = 30 #duração cada bloco
    isozona = "D"
    tr_df = pd.read_pickle("Pr_Tr.pkl")

    project_rain = Taborga(tr_df, isozona="D", coef_Taborga_24h = 1.1, tc = tc, d = d)
    hiet_proj  = Hyetograph(project_rain)
#%%
    Taborga_1_24 = pd.read_pickle("Taborga_Coef_1h_24h.pkl")
    Taborga_6_24 = pd.read_pickle("Taborga_Coef_6min_24h.pkl")
    trs = tr_df.columns
    isozona = "D"
    P24h_tr = tr_df * 1.1
    P1h_tr = P24h_tr * Taborga_1_24.loc[isozona, trs]
    P6m_tr = P24h_tr * Taborga_6_24.loc[isozona, trs]
    d = 30
    tc = (tc + d) - ((tc + d) % d) 




    project_rain = pd.DataFrame([], index = np.arange(d, tc + d, d))
    for tr in trs:
        P6m = P6m_tr[tr].values[0]
        P1h = P1h_tr[tr].values[0]
        P24h = P24h_tr[tr].values[0]

        for t in project_rain.index:
            project_rain.loc[t, tr] = get_pr_values(t, P6m, P1h, P24h)


    inc_pr = project_rain.diff()
    inc_pr.iloc[0,:] = project_rain.iloc[0,:]
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
    hiet_proj.to_pickle("Hietogramas_Projeto.pkl")


    
    fig, ax = plt.subplots(dpi = 600)
    ax.bar(x = hiet_proj.index, height= hiet_proj[50], width = 20)


    fig, ax = plt.subplots(dpi = 600)
    ax.plot([np.log(6), np.log(60), np.log(1440)], [P6m, P1h, P24h])
    ax.scatter(np.log(project_rain.index), project_rain[50], color = "red", zorder = 3)


#%%


#%%