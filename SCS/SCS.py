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
import os
warnings.simplefilter(action='ignore', category=FutureWarning)

def Kirpich(L, hf, hi):
    
    tc = 57*np.power((np.power(L,3)/(hi-hf)), 0.385)
    
    return tc

def Kirpich_modificado(L, hf, hi):
    
    tc = 85.2*np.power((np.power(L,3)/(hi-hf)), 0.385)

    return tc

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
        #Achando os valores imediatamentes superior e inferior
        upper_t = t_tp[t_tp >= ratio_t].min()
        lower_t = t_tp[t_tp <= ratio_t].max()
        upper_q = Dim_HU["q_qp"].loc[Dim_HU["t_tp"] == upper_t].values[0]
        lower_q = Dim_HU["q_qp"].loc[Dim_HU["t_tp"] == lower_t].values[0]

        #interpolação linear do ratio_q
        ratio_q = lower_q + (ratio_t-lower_t)*((upper_q-lower_q)/(upper_t - lower_t))

        q = ratio_q*HU["qp"]
    
    return q

def CN_SCS (CN, hietograma):
    tempo = hietograma["tempo"]
    pef_dict = {}
    for i in info_prec.columns[1:]:
        pr_inc = info_prec[i]

        S = (25400/CN) - 254

        pr_acc = pr_inc.cumsum() #Acumulado ordenado segundo o hietograma
        
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
    
    #Cada bloco do HU aumenta 1 linha do tamanho do hietograma
    #O -1 é pq o primeiro bloco não conta
    matrix_pef = np.full((len(pef_df)+ (HU_intervals-1), HU_intervals), np.nan)
    
    #Criando a matriz com repetição do hietograma de pef
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

info_df = pd.read_excel("Info_BH.xlsx", sheet_name = "List_BH")
info_prec = pd.read_excel("hietogramas.xlsx", sheet_name = "24horas")
Dim_HU = pd.read_csv("Dimensionless_UH.csv", sep = "\t")

create_outputfile()

d = info_prec["tempo"][1] - info_prec["tempo"][0]


for i in range(len(info_df)):
    name = info_df["Nome"][i]
    area = info_df["Area"][i]
    hi = info_df["hi"][i]
    hf = info_df["hf"][i]
    Le = info_df["L"][i]
    CN = info_df["CN"][i]

    # tc = Kirpich(Le, hf, hi)
    tc = Kirpich_modificado(Le, hf, hi)

    # HU = HU_SCS(area, tc/60, d)
    HU = Curv_HU_SCS(area, tc, d)
    pef_df = CN_SCS(CN, info_prec)

    for tr in pef_df.columns[1:]:
        pef = pef_df[tr]
        Q = Conv_HU(pef, HU, d)
        if tr == pef_df.columns[1]:
            Q_df = pd.DataFrame({"{}".format(tr): Q[:,0]})
        else:
            Q_df[tr] = Q[:,0]

    Q_df.index = list(range(0, Q.shape[0]*d, d))
    write_outputfile(Q_df, name)
        


