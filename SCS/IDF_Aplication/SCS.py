#%%
'''
Autor: Carlos Eduardo Sousa Lima, M. Sc
e-mail: carlosesl07@gmail.com
Departamento de Engenharia Hidráulica e Ambiental/ Universidade Federal do Ceará (DEHA/UFC)
Doutorando em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Mestre em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Engenheiro Civil com ênfase em Meio Ambiente - Universidade Estadual Vale do Acaraú (UVA)
'''

import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import project_hyetograph
import time_of_concetration
import os
warnings.simplefilter(action='ignore', category=FutureWarning)


def HU_SCS(area, tc, d):

    tlag = 0.6*tc
    tp = tlag + 0.5*d
    tb = 2.67*tp
    qp = (0.208*area)/(tp/60)

    return ({"tlag": tlag, "tp": tp, "tb": tb, "qp": qp})

def Curv_HU_SCS(area, tc, d):

    tlag = 0.6*tc
    tp = tlag + 0.5*d
    tb = 5*tp
    qp = (0.208*area)/(tp/60)

    return ({"tlag": tlag, "tp": tp, "tb": tb, "qp": qp})

def get_HU_value(t, HU):

    if t <= HU["tp"]:
        t0 = 0
        q0 = 0
        t1 = HU["tp"]
        q1 = HU["qp"]
    else:
        t0 = HU["tp"]
        q0 = HU["qp"]
        t1 = HU["tb"]
        q1 = 0
    
    if t < HU["tb"]:
        q = q0 + ((t-t0)/(t1-t0))*(q1-q0)
    else:
        q = 0

    return q

def get_Curve_HU_value(t, HU, Dim_HU):
    
    t_tp = np.array(Dim_HU["t_tp"])

    ratio_t = t/HU["tp"]

    
    if (t > HU["tb"]) | (t == 0):
        q = 0

    else:

        if ratio_t in t_tp: #Valor exato
            ratio_q = Dim_HU["q_qp"].loc[Dim_HU["t_tp"] == ratio_t].values[0]
        
        else: #Interpolar

            #Achando os valores imediatamentes superior e inferior
            upper_t = t_tp[t_tp > ratio_t].min()
            lower_t = t_tp[t_tp < ratio_t].max()
            upper_q = Dim_HU["q_qp"].loc[Dim_HU["t_tp"] == upper_t].values[0]
            lower_q = Dim_HU["q_qp"].loc[Dim_HU["t_tp"] == lower_t].values[0]

            #interpolação linear do ratio_q
            ratio_q = lower_q + (ratio_t-lower_t)*((upper_q-lower_q)/(upper_t - lower_t))

        q = ratio_q*HU["qp"]
    
    return q

def CN_SCS (CN, hyetograph):
    tempo = hyetograph.index
    pef_dict = {}
    for i in hyetograph.columns[0:]:
        pr_inc = hyetograph[i]

        S = (25400/CN) - 254

        pr_acc = pr_inc.cumsum() #Acumulado ordenado segundo o hyetograph
        
        pef_list = []
        
        for x in pr_acc:
            if x >= 0.2*S:
                pef_list.append(np.power(x-0.2*S,2)/(x+0.8*S))
            else:
                pef_list.append(0)
        
        pef_dict[i] = pef_list

    pef_acc = pd.DataFrame(pef_dict) #Acumulada
    pef_inc = pef_acc.diff() #INcremental
    pef_inc.iloc[0,:] = pef_acc.iloc[0,:]
    pef_inc.insert(0, "tempo", tempo)
    
    return pef_inc

def Conv_HU (pef, HU, d):

    # 4 blocos a mais para sempre chegar no zero
    # HU em função do múltiplo mais próximo da duração
    HU_intervals = int(((round((HU["tb"]+d)/d)) * d)/d) + 4
    HU_q = np.full((HU_intervals, 1), np.nan)
    for i in range(HU_intervals):
        HU_q[i] = get_Curve_HU_value(i*d, HU, Dim_HU)
    #Cada bloco do HU aumenta 1 linha do tamanho do hyetograph
    #O -1 é pq o primeiro bloco não conta
    matrix_pef = np.full((len(pef_df)+ (HU_intervals-1), HU_intervals), np.nan)
    
    #Criando a matriz com repetição do hyetograph de pef
    #Sempre defasados em uma linha
    for i in range(matrix_pef.shape[1]):
        for j in range(len(pef)):
            matrix_pef[i+j, i] = pef[j]
    
    matrix_pef[np.isnan(matrix_pef)] = 0
    Q = np.dot(matrix_pef, HU_q) 

    return Q

def create_outputfile():

    if os.path.exists("Output_SCS.xlsx"):
        os.remove("Output_SCS.xlsx")
    df = pd.DataFrame([])

    with pd.ExcelWriter('Output_SCS.xlsx', mode='w') as writer:
        df.to_excel(writer)

    return ("Arquivo de saída criado (.xlsx)")

def write_outputfile(df, name):

    with pd.ExcelWriter('Output_SCS.xlsx', mode='a') as writer:
        df.to_excel(writer, sheet_name = name)

    return ("{} simulada(o)".format(name))

#%%
Dim_HU = pd.read_pickle("Dimensionless_UH.pkl")

info_df = pd.read_excel("Info_BH.xlsx", sheet_name = "List_BH")
trs = [10, 25,50, 100]

create_outputfile()

#%%
for i in range(len(info_df)):
    name = info_df["Bacia"][i]
    area = info_df["Area"][i] #para km²
    tc = info_df["tc"][i]
    CN = info_df["CN"][i]
    du = info_df["Dur_Chuva"][i]
    inc_du = info_df["inc_time"][i]

    project_rain = project_hyetograph.prj_rain_IDF(
        a = 918.8,
        b = 0.171,
        c = 9.19,
        d = 0.706,
        du = du, inc_du = inc_du,
        trs = trs)
    
    hyetograph = project_hyetograph.Hyetograph(project_rain)

    HU = Curv_HU_SCS(area, du, inc_du)
    pef_df = CN_SCS(CN, hyetograph)

    for tr in pef_df.columns[1:]:
        pef = pef_df[tr]
        Q = Conv_HU(pef, HU, inc_du)
        if tr == pef_df.columns[1]:
            Q_df = pd.DataFrame({"{}".format(tr): Q[:,0]})
        else:
            Q_df[tr] = Q[:,0]

    Q_df.index = list(range(0, Q.shape[0]*inc_du, inc_du))
    print(name)
    print(Q_df.max())
    write_outputfile(Q_df, name)

#%%
fig, ax = plt.subplots(dpi = 600)
ax.plot(Q_df, label = Q_df.columns)
ax.legend()
ax.set_ylabel("Vazão (m³/s)")
# %%
