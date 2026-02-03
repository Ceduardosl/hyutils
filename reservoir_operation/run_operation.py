import pandas as pd
import numpy as np
import reservoir_operations as res_opr
from scipy.optimize import minimize_scalar

#%%
inflow = pd.read_pickle("Afluencia_mcs.pkl")
cav = pd.read_pickle("CAV_Congonhas.pkl")
evap = pd.read_pickle("Evap_mm.pkl")

evap_array = np.tile(evap, int(len(inflow)/len(evap))).flatten(order = "F").reshape(-1,1)
evap_array = np.append(evap_array, evap.values[0:3], axis = 0)
evap_array = evap_array.reshape(-1)

#%%

#cs = crest elevatio
#cap = storage capacity

a, b = res_opr.get_alpha_beta(cav["Area"].values, cav["Volume"].values)

cs = 926

storage_cap = res_opr.get_cap(cav["Cota"].values, cav["Volume"].values, cs)

Q90 = minimize_scalar(res_opr.optimize_operation,
                        bounds = [np.mean(inflow), 4 * np.mean(inflow)],
                        args = (storage_cap,
                                storage_cap/2,
                                inflow,
                                evap_array,
                                a,
                                b,
                                0.9))

Q99 = minimize_scalar(res_opr.optimize_operation,
                        bounds = [np.mean(inflow), 4 * np.mean(inflow)],
                        args = (storage_cap,
                                storage_cap/2,
                                inflow,
                                evap_array,
                                a,
                                b,
                                0.99))
#%%
operation = res_opr.mon_operation(Q_reg = Q90,
                        max_storage = storage_cap,
                        S0 = storage_cap/2,
                        inflow = inflow,
                        evap = evap_array)

#S0 = Initial Storage hm³
#Qin = Inflow
#mon_evap = Monthly net evaporation
#Er1 = Evaporation loss – first portion
#Re1 = Regularization loss - first portion
#S1 = Storage after initial losses
#Er2 = Evaporation loss - second portion
#Re2 = Regularization loss - second portion
#Sf = Final storage
#Qout = outflow

df_operation = pd.DataFrame(operation, columns = ["S0", "Qin", "mon_evap", "Er1", "Re1", "S1", "Er2", "Re2", "Sf", "Qout"])
df_operation.index = inflow.index

#all units in hm³ or hm³/month, except mon_evapo (meter)
#Si, Qin, Evap, Er1, Re1, V2, Evap2, Re2, Sf, Vert
