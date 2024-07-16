'''
Autor: Carlos Eduardo Sousa Lima, M. Sc
e-mail: carlosesl07@gmail.com
Departamento de Engenharia Hidráulica e Ambiental/ Universidade Federal do Ceará (DEHA/UFC)
Doutorando em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Mestre em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Engenheiro Civil com ênfase em Meio Ambiente - Universidade Estadual Vale do Acaraú (UVA)
'''
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import warnings
import os
warnings.simplefilter(action='ignore', category=FutureWarning)
# pd.set_option('mode.chained_assignment', None)

def outflow_spilway(H, C, L, H0):

    if H - H0 >= 0:
        Q_out = C*L*np.power(H-H0, 3/2)
    else:
        Q_out = 0
    return Q_out

def linear_interpolation(df, x):

    columns = df.columns
    y_arr = np.array(df.iloc[:,0])
    x_arr = np.array(df.iloc[:,1])

    if x >= max(x_arr):
        print("Interpolar mais valores da CAV")

    upper_x = x_arr[x_arr > x].min()
    lower_x = x_arr[x_arr < x].max()

    upper_y = df[columns[0]].loc[df[columns[1]] == upper_x].values[0]
    lower_y = df[columns[0]].loc[df[columns[1]] == lower_x].values[0]

    y = lower_y + (x - lower_x)*((upper_y-lower_y)/(upper_x - lower_x))

    return y

def Table_CAV_outflow (CAV_data, H0, C, L):

    CAV_outflow = CAV_data.copy()
    CAV_outflow["outflow"] = CAV_outflow["Cota"].apply(lambda x: outflow_spilway(x, C, L, H0) )
    CAV_outflow["puls_right"] = (2*CAV_outflow["Volume"])/dt + CAV_outflow["outflow"]

    return CAV_outflow

def Modified_Puls(df, CAV_outflow, H0, C, L, H_ini):

    puls_matrix = np.full((df.shape[0], 11), np.nan)
    puls_matrix[:,0] = df["tempo"]

    for i in range(0, puls_matrix.shape[0]):
        if i == 0:
            puls_matrix[:,1] = df.iloc[:,1]
            puls_matrix[:-1,2] = puls_matrix[1:,1]
            puls_matrix[-1,2] = 0
            puls_matrix[0,3] = H_ini #H_ini
            puls_matrix[0,4] = CAV_outflow["Volume"].loc[CAV_outflow["Cota"] == H0]
            puls_matrix[0,5] = outflow_spilway(puls_matrix[0,3], C, L, H0) #Q t+0
            puls_matrix[0,6] = ((2*puls_matrix[0,4]/dt) - puls_matrix[0,5]) + puls_matrix[0,1] + puls_matrix[0,2]
            puls_matrix[0,7] = puls_matrix[0,6]
            if puls_matrix[0,7] in CAV_outflow["puls_right"].values: #H t+1
                puls_matrix[0,8] = CAV_outflow["Cota"].loc[CAV_outflow["puls_right"] == puls_matrix[0,7]]
            else:
                puls_matrix[0,8] = linear_interpolation(CAV_outflow[["Cota", "puls_right"]], x = puls_matrix[0,7])
            puls_matrix[0,9] = outflow_spilway(puls_matrix[0,8], C, L, H0) #Q t+1
            puls_matrix[0,10] = (puls_matrix[0,7] - puls_matrix[0,9])*(dt/2) #S t+1
        
        else:
            puls_matrix[i,3] = puls_matrix[i-1,8]
            puls_matrix[i,4] = puls_matrix[i-1, 10]
            puls_matrix[i,5] = puls_matrix[i-1, 9]
            puls_matrix[i,6] = ((2*puls_matrix[i,4]/dt) - puls_matrix[i,5]) + puls_matrix[i,1] + puls_matrix[i,2]
            puls_matrix[i,7] = puls_matrix[i,6]
            if puls_matrix[i,7] in CAV_outflow["puls_right"].values:
                puls_matrix[i,8] = CAV_outflow["Cota"].loc[CAV_outflow["puls_right"] == puls_matrix[i,7]]
            else:
                puls_matrix[i,8] = linear_interpolation(CAV_outflow[["Cota", "puls_right"]], x = puls_matrix[i,7])
            puls_matrix[i,9] = outflow_spilway(puls_matrix[i,8], C, L, H0) #Q t+1
            puls_matrix[i,10] = (puls_matrix[i,7] - puls_matrix[i,9])*(dt/2) #S t+1

        puls_df = pd.DataFrame(puls_matrix,
            columns = ["time", "I_t", "I_t+1", "H_t", "S_t", "Q_t",
                "puls_left", "puls_right", "H_t+1", "Q_t+1", "S_t+1"])
        
        hydrographs_df = puls_df[["I_t", "Q_t"]]
        hydrographs_df.columns = ["Inflow", "Outflow"]

    return ([puls_df, hydrographs_df])

def create_outputfile(path):

    if os.path.exists(path):
        os.remove(path)
    df = pd.DataFrame([])

    with pd.ExcelWriter(path, mode='w') as writer:
        df.to_excel(writer)

    return ("Arquivo de saída criado - {}".format(path))
#%%
scenario = ["Base", "CEN1", "CEN2"]

for sc in scenario:

    list_bh = glob("input/{}/*.xlsx".format(sc))

    for path in list_bh:
        print("{} - Iniciado".format(path))
        name = path.split("\\")[-1].split(".")[0]
        path_output1 = "output/{}/{}.xlsx".format(sc, name) #Tabela do Puls
        path_output2 = "output_hydrographs/{}/{}.xlsx".format(sc, name) #Hidrogramas
        create_outputfile(path_output1)
        create_outputfile(path_output2)


        spillway_data = pd.read_excel(path, sheet_name = "Spillway")
        CAV_data = pd.read_excel(path, sheet_name = "CAV")
        inflow_data = pd.read_excel(path, sheet_name = "Inflow")
        dt = (inflow_data["tempo"][1] - inflow_data["tempo"][0]) * 60

        C = spillway_data["C"][0]
        L = spillway_data["L"][0]
        H0 = spillway_data["H0"][0]
        CAV_outflow = Table_CAV_outflow(CAV_data, H0, C, L)

        with pd.ExcelWriter(path_output1, mode = "a") as out1, pd.ExcelWriter(path_output2, mode = "a") as out2:
            hydrographs_df = pd.DataFrame()
            for tr in inflow_data.columns[1:]:
                inflow = inflow_data[["tempo", tr]]
                puls_matrix, hydrographs = Modified_Puls(inflow, CAV_outflow, H0, C, L, H_ini = H0)
                
                if tr == inflow_data.columns[1:][0]:
                    hydrographs = hydrographs.add_suffix("_{}".format(tr))
                    hydrographs_df = hydrographs
                
                else:
                    hydrographs = hydrographs = hydrographs.add_suffix("_{}".format(tr))
                    hydrographs_df = hydrographs_df.merge(hydrographs, right_index = True, left_index = True)
                puls_matrix.to_excel(out1, sheet_name = tr, index = False)
            hydrographs_df.insert(0, "tempo", inflow["tempo"])
            hydrographs_df.to_excel(out2, sheet_name = "Streamflows", index = False)

        print("{} - Finalizado".format(path))
# %%

#%%
# H_ini = H0
# S_ini = CAV_outflow["Volume"].loc[CAV_outflow["Cota"] == H0]
# Q_ini = outflow_spilway(H_ini, C, L, H0)

# puls_matrix = np.full((inflow_data.shape[0], 11), np.nan)
# puls_matrix[:,0] = inflow_data["tempo"]
# for i in range(0, puls_matrix.shape[0]):
#     if i == 0:
#         puls_matrix[:,1] = inflow_data["Tr = 5 anos"]
#         puls_matrix[:-1,2] = puls_matrix[1:,1]
#         puls_matrix[-1,2] = 0
#         puls_matrix[0,3] = H0 #H_ini
#         puls_matrix[0,4] = CAV_outflow["Volume"].loc[CAV_outflow["Cota"] == H0]
#         puls_matrix[0,5] = outflow_spilway(puls_matrix[0,3], C, L, H0) #Q t+0
#         puls_matrix[0,6] = ((2*puls_matrix[0,4]/dt) - puls_matrix[0,5]) + puls_matrix[0,1] + puls_matrix[0,2]
#         puls_matrix[0,7] = puls_matrix[0,6]
#         if puls_matrix[0,7] in CAV_outflow["puls_right"].values: #H t+1
#             puls_matrix[0,8] = CAV_outflow["Cota"].loc[CAV_outflow["puls_right"] == puls_matrix[0,7]]
#         else:
#             puls_matrix[0,8] = linear_interpolation(CAV_outflow[["Cota", "puls_right"]], x = puls_matrix[0,7])
#         puls_matrix[0,9] = outflow_spilway(puls_matrix[0,8], C, L, H0) #Q t+1
#         puls_matrix[0,10] = (puls_matrix[0,7] - puls_matrix[0,9])*(dt/2) #S t+1
    
#     else:
#         puls_matrix[i,3] = puls_matrix[i-1,8]
#         puls_matrix[i,4] = puls_matrix[i-1, 10]
#         puls_matrix[i,5] = puls_matrix[i-1, 9]
#         puls_matrix[i,6] = ((2*puls_matrix[i,4]/dt) - puls_matrix[i,5]) + puls_matrix[i,1] + puls_matrix[i,2]
#         puls_matrix[i,7] = puls_matrix[i,6]
#         if puls_matrix[i,7] in CAV_outflow["puls_right"].values:
#             puls_matrix[i,8] = CAV_outflow["Cota"].loc[CAV_outflow["puls_right"] == puls_matrix[i,7]]
#         else:
#             puls_matrix[i,8] = linear_interpolation(CAV_outflow[["Cota", "puls_right"]], x = puls_matrix[i,7])
#         puls_matrix[i,9] = outflow_spilway(puls_matrix[i,8], C, L, H0) #Q t+1
#         puls_matrix[i,10] = (puls_matrix[i,7] - puls_matrix[i,9])*(dt/2) #S t+1

# puls_df = pd.DataFrame(puls_matrix,
#         columns = ["time", "I_t", "I_t+1", "H_t", "S_t", "Q_t",
#             "puls_left", "puls_right", "H_t+1", "Q_t+1", "S_t+1"])

# hydrographs_df = puls_df[["time", "I_t", "Q_t"]]
#%%

#%%
# from scipy.interpolate import splrep, BSpline
# #%%
# x = hydrographs_df["time"]
# x_new = np.linspace(min(x), max(x), 100)
# y_in = hydrographs_df["I_t"]
# y_out = hydrographs_df["Q_t"]
# tck_in = splrep(x, y_in, s=0)
# tck_out = splrep(x, y_out, s=0)

# fig, ax = plt.subplots()
# # ax.plot(hydrographs_df["time"], hydrographs_df["I_t"])
# ax.plot(x_new, BSpline(*tck_in)(x_new), zorder = 2, lw = 2)
# ax.plot(x_new, BSpline(*tck_out)(x_new), zorder = 2, lw = 2)
# ax.axhline(y = 0, ls = "-", c = "black", zorder = 1)
# ax.set_title("")
# # ax.plot(hydrographs_df["time"], hydrographs_df["Q_t"])



#%%
# %%

# %%
