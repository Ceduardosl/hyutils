import pandas as pd
import numpy as np
import reservoir_operations as res_opr
from scipy.optimize import minimize_scalar
import os
def annual_storage_variation(group):
    
        initial_storage = group.loc[group.index.month == 1, "S0"]
        final_storage = group.loc[group.index.month == 12, "Sf"]

        if not initial_storage.empty and not final_storage.empty:
                return initial_storage.iloc[0] - final_storage.iloc[-1]
        else:
                return

def get_summary_operation(cs, Q_reg, max_storage, S0, inflow, evap, alpha, beta, label_permanence):
        
        operation = res_opr.mon_operation(Q_reg,
                        max_storage,
                        S0,
                        inflow,
                        evap,
                        alpha,
                        beta)

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
        #all units in hm³ or hm³/month, except mon_evapo (meter)
        #Si, Qin, Evap, Er1, Re1, V2, Evap2, Re2, Sf, Vert
        df_operation = pd.DataFrame(operation, columns = ["S0", "Qin", "mon_evap", "Er1", "Re1", "S1", "Er2", "Re2", "Sf", "Qout"])
        df_operation.index = inflow.index

        if not os.path.exists("operation_output"):
                os.makedirs("operation_output")

        df_operation.to_csv("operation_output/{}_mon_operation_cs_{}.csv".format(label_permanence, cs), index = True, header = True)

        storage_variation = df_operation.groupby(df_operation.index.year).apply(annual_storage_variation)
        storage_variation.index = df_operation.resample("YS").count().index
        
        annual_operation = pd.DataFrame({
        "Qin": df_operation["Qin"].resample("YS").sum(),
        "Delta_S": storage_variation,
        "Er": df_operation["Er1"].resample("YS").sum() + \
                df_operation["Er2"].resample("YS").sum(),
        "Reg": df_operation["Re1"].resample("YS").sum() + \
                df_operation["Re2"].resample("YS").sum(),
        "Qout": df_operation["Qout"].resample("YS").sum()
        })

        annual_operation = annual_operation.loc[annual_operation.index.year <= 2023]

        mon_NA = np.interp(df_operation["S0"], cav["Volume"].values, cav["Cota"].values)

        outputlist = [cs, Q_reg,
                annual_operation["Qin"].mean() + annual_operation["Delta_S"].mean(),
                annual_operation["Reg"].mean(), annual_operation["Er"].mean(),
                annual_operation["Qout"].mean(), np.median(mon_NA)]
        
        return outputlist
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

output_Q90 = []
output_Q99 = []

for cs in range(900, 930+1, 1):
        
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

        output_Q90.append(get_summary_operation(cs, 
                                Q90.x, 
                                max_storage = storage_cap,
                                S0 = storage_cap/2,
                                inflow = inflow,
                                evap = evap_array,
                                alpha = a,
                                beta = b, label_permanence = "Q90"))
        output_Q99.append(get_summary_operation(cs, 
                                Q99.x, 
                                max_storage = storage_cap,
                                S0 = storage_cap/2,
                                inflow = inflow,
                                evap = evap_array,
                                alpha = a,
                                beta = b, label_permanence = "Q99"))

#%%

df_Q90 = pd.DataFrame(output_Q90,
                columns = ["Cota da Soleira",
                "Q_reg (hm³/mês)",
                "Produção (hm³)",
                "Volume Regularizado (hm³)",
                "Volume Evaporado (hm³)",
                "Volume Vertido (hm³)",
                "Mediana NA (m)"
                        ])


df_Q90.to_csv("summary_Q90_operation.csv", index = None, header = True)

df_Q99 = pd.DataFrame(output_Q99,
                columns = ["Cota da Soleira",
                "Q_reg (hm³/mês)",
                "Produção (hm³)",
                "Volume Regularizado (hm³)",
                "Volume Evaporado (hm³)",
                "Volume Vertido (hm³)",
                "Mediana NA (m)"
                        ])

df_Q99.to_csv("summary_Q99_operation.csv", index = None, header = True)


#%%
