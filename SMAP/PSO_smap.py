#%%
'''
Autor: Carlos Eduardo Sousa Lima, M. Sc
e-mail: carlosesl07@gmail.com
Departamento de Engenharia Hidráulica e Ambiental/ Universidade Federal do Ceará (DEHA/UFC)
Doutorando em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Mestre em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Engenheiro Civil com ênfase em Meio Ambiente - Universidade Estadual Vale do Acaraú (UVA)
'''
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import smapm
from pyswarms.single.global_best import GlobalBestPSO
import pandas as pd
from sklearn.metrics import r2_score, root_mean_squared_error

#%%
# def get_FO(x, fixed_params, area, pr, pet, q_obs):
#     FO = []
#     # fixed_params = [tuin, ebin]
#     for params in x:
#         q_sim = smapm.smapm(params, fixed_params, area, pr, pet)
#         FO.append(-r2_score(q_obs[warm:], q_sim[warm:]))
#         # FO.append(root_mean_squared_error(q_obs[:], q_sim[:]))

#     return FO

def get_FO(x, area, pr, pet, q_obs, warm):
    FO = []
    # fixed_params = [tuin, ebin]
    for params in x:
        q_sim = smapm.smapm(params, area, pr, pet)
        FO.append(-r2_score(q_obs[warm:], q_sim[warm:]))
        # FO.append(root_mean_squared_error(q_obs[:], q_sim[:]))

    return FO
def get_PBIAS(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()
    diff = y_true - y_hat
    PBIAS = np.sum(diff)/np.sum(y_true)

    return (PBIAS*100)

def get_NSE(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    NSE = r2_score(y_true, y_hat)

    return NSE

def get_KGE(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    R = np.corrcoef(y_true, y_hat)[1,0]

    mean_ratio = np.sum(y_true)/np.sum(y_hat)

    CV_true = np.std(y_true, ddof = 1)/np.mean(y_true)
    CV_hat = np.std(y_hat, ddof = 1)/np.mean(y_hat)

    CV_ratio = CV_hat/CV_true

    KGE = 1 - np.power(
    np.power((R-1),2) + 
    np.power((mean_ratio - 1),2) + 
    np.power((CV_ratio - 1),2), 0.5)

    return KGE

def get_RMSE(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    diff_quad = np.power(y_true - y_hat,2)
    
    RMSE = np.power(diff_quad.sum()/len(y_true), 0.5)

    return RMSE

def get_corrcoef(y_true, y_hat):

    if y_true.ndim > 1:
        y_true = y_true.flatten()
    if y_hat.ndim > 1:
        y_hat = y_hat.flatten()

    R = np.corrcoef(y_true, y_hat)[1,0]

    return R

#%%
epq_df = pd.read_excel("SMAP_5305.xlsx", sheet_name = "P2", index_col = 0)
epq_df.index = pd.to_datetime(epq_df.index)


#%%
q_train = epq_df["Q"].to_numpy().flatten()
pr_train = epq_df["P"].to_numpy().flatten()
pet_train = epq_df["ETP"].to_numpy().flatten()


#%%
warm = 12

bnd_params = (np.array([400, 0.1, 0, 1, 0, 0]), 
              np.array([5000, 10, 70, 6, 100, 100]))
# const_params = [30, 0]
options = {'c1': 1.5, 'c2': 1.5, 'w': 0.9}
optimizer = GlobalBestPSO(n_particles=50, dimensions=6 , options=options, bounds=bnd_params)
# cost, pos = optimizer.optimize(get_FO, iters = 250, fixed_params = const_params,
#             area = 626.893179, 
#             pr = pr_train, pet = pet_train, q_obs = q_train)
cost, pos = optimizer.optimize(get_FO, iters = 250,
            area = 626.893179, 
            pr = pr_train, pet = pet_train, q_obs = q_train, warm = warm)

#%%
P1_df = pd.read_excel("SMAP_5305.xlsx", sheet_name = "P1", index_col = 0)
P1_df.index = pd.to_datetime(P1_df.index)

P2_df = pd.read_excel("SMAP_5305.xlsx", sheet_name = "P2", index_col = 0)
P2_df.index = pd.to_datetime(P2_df.index)

P3_df = pd.read_excel("SMAP_5305.xlsx", sheet_name = "P3", index_col = 0)
P3_df.index = pd.to_datetime(P3_df.index)

P4_df = pd.read_excel("SMAP_5305.xlsx", sheet_name = "P4", index_col = 0)
P4_df.index = pd.to_datetime(P4_df.index)

#%%
P1_sim = smapm.smapm(pos, area = 626.893179,
                     prec = P1_df.P.to_numpy(),
                     pet = P1_df.ETP.to_numpy())

P2_sim = smapm.smapm(pos, area = 626.893179,
                     prec = P2_df.P.to_numpy(),
                     pet = P2_df.ETP.to_numpy())

P3_sim = smapm.smapm(pos, area = 626.893179,
                     prec = P3_df.P.to_numpy(),
                     pet = P3_df.ETP.to_numpy())

P4_sim = smapm.smapm(pos, area = 626.893179,
                     prec = P4_df.P.to_numpy(),
                     pet = P4_df.ETP.to_numpy())


P1_out = P1_df[["Q"]].copy()
P1_out["q_sim"] = P1_sim

P2_out = P2_df[["Q"]].copy()
P2_out["q_sim"] = P2_sim

P3_out = P3_df[["Q"]].copy()
P3_out["q_sim"] = P3_sim

P4_out = P4_df[["Q"]].copy()
P4_out["q_sim"] = P4_sim

P1_out.to_csv("sim_streamflow/5305_P1.csv", index = True, header = True)
P2_out.to_csv("sim_streamflow/5305_P2.csv", index = True, header = True)
P3_out.to_csv("sim_streamflow/5305_P3.csv", index = True, header = True)
P4_out.to_csv("sim_streamflow/5305_P4.csv", index = True, header = True)

#%%
opt_coef = pd.DataFrame(pos,
index = ["sat", "pes", "crec", "k", "tuin", "ebin"])

opt_coef.to_csv("opt_coef_5305.csv", index = True, header = 5305)

metrics_df = pd.DataFrame(
    [
    [
        get_corrcoef(P1_df.Q.to_numpy()[warm:], P1_sim[warm:]), 
        get_corrcoef(P2_df.Q.to_numpy()[warm:], P2_sim[warm:]),
        get_corrcoef(P3_df.Q.to_numpy()[warm:], P3_sim[warm:]),
        get_corrcoef(P4_df.Q.to_numpy()[warm:], P4_sim[warm:])
    ],

    [
        get_RMSE(P1_df.Q.to_numpy()[warm:], P1_sim[warm:]), 
        get_RMSE(P2_df.Q.to_numpy()[warm:], P2_sim[warm:]),
        get_RMSE(P3_df.Q.to_numpy()[warm:], P3_sim[warm:]),
        get_RMSE(P4_df.Q.to_numpy()[warm:], P4_sim[warm:])
    ],

    [
        get_PBIAS(P1_df.Q.to_numpy()[warm:], P1_sim[warm:]), 
        get_PBIAS(P2_df.Q.to_numpy()[warm:], P2_sim[warm:]),
        get_PBIAS(P3_df.Q.to_numpy()[warm:], P3_sim[warm:]),
        get_PBIAS(P4_df.Q.to_numpy()[warm:], P4_sim[warm:])
    ],

    [
        get_NSE(P1_df.Q.to_numpy()[warm:], P1_sim[warm:]), 
        get_NSE(P2_df.Q.to_numpy()[warm:], P2_sim[warm:]),
        get_NSE(P3_df.Q.to_numpy()[warm:], P3_sim[warm:]),
        get_NSE(P4_df.Q.to_numpy()[warm:], P4_sim[warm:])
    ],

    [
        get_KGE(P1_df.Q.to_numpy()[warm:], P1_sim[warm:]), 
        get_KGE(P2_df.Q.to_numpy()[warm:], P2_sim[warm:]),
        get_KGE(P3_df.Q.to_numpy()[warm:], P3_sim[warm:]),
        get_KGE(P4_df.Q.to_numpy()[warm:], P4_sim[warm:])
    ]],

    columns = ["P1", "P2", "P3", "P4"],
    index = ["corr", "RMSE", "PBIAS", "NSE", "KGE"]
)

metrics_df.to_csv("metrics_5305.csv", index = True, header = True)
#%%


#%%