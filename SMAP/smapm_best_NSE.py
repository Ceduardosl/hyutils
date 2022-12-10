# -*- coding: utf-8 -*-
#Finds the time series interval that maximizes the NSE
__author__ = "Carlos Eduardo Sousa Lima"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "eduardolima@alu.ufc.br"
__maintainer__ = "Carlos Eduardo Sousa Lima"
__status__ = "Production"
#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

#%%
def smapm(area, para, prec, pet):
    # smapm function by:
    # author = ["Paulo Jarbas Camurca"]
    # credits = ["Fco Vasconcelos", "Marcelo Rodrigues"]
    # license = "GPL"
    # version = "1.0"
    # email = "pjarbas312@gmail.com"
    """
    :param para: Smap parameters and basin area.
    :param prec: Precipitation timeseries.
    :param pet: Potential Evapotranspiration. 

    """

    # check nan and inf values in pet e prec arrays
    if np.any(np.isnan(prec)) or np.any(np.isnan(pet)):
        print ('Nan values found, exiting...')
        exit()

    if np.any(np.isinf(prec)) or np.any(np.isinf(pet)):
        print ('Inf values found, exiting...')
        exit()

    area = area
    #m = len(para)  # 2 ou 6 parametros
    e = pet
    n = len(prec)
    sat = para[0]
    pes = para[1]
    crec = para[2]
    crecp = crec/100.
    k = para[3]
    # Evitar divisão por zero para valores de k = 0
    if k==0:
        ke = 0
    else:
        ke = np.power(0.5,(1/k))
    tuin = para[4]
    tuinp = tuin/100.
    ebin = para[5]

    rsol,rsub,tu = np.zeros((n+1)) * 0.,np.zeros((n+1)) * 0.,np.zeros((n+1)) * 0.
    dsol,es,er = np.zeros((n+1)) * 0.,np.zeros((n+1)) * 0.,np.zeros((n+1)) * 0.
    rec,eb,qcalc= np.zeros((n+1)) * 0.,np.zeros((n+1)) * 0.,np.zeros((n)) * 0.

    for i in range(n+1):
        if i==0:
            rsol[i] = tuinp*sat
            rsub[i] = ebin/(1-ke)/area*2630.
            tu[i] = tuinp
        else:
            if prec[i-1] == -999:
                qcalc[i-1] = np.nan
                continue

            dsol[i] = 0.5*(prec[i-1] - prec[i-1]*(np.power(tu[i-1],pes)) - e[i-1]*tu[i-1] - rsol[i-1]*crecp*(np.power(tu[i-1],4)))
            tu[i] = (rsol[i-1] + dsol[i])/sat
            es[i] = prec[i-1]*np.power(tu[i],pes)
            er[i] = e[i-1]*tu[i]
            rec[i] = rsol[i-1]*crecp*np.power(tu[i],4)
            eb[i] = rsub[i-1]*(1-ke)
            rsub[i] = rsub[i-1] - eb[i] + rec[i]
            rsol[i] = rsol[i-1] + prec[i-1] - es[i] - er[i] - rec[i]
            qcalc[i-1]=(es[i] + eb[i])*area/2630.

    # replace nan and inf values by -999
    qcalc[np.where(np.isnan(qcalc))] = -999.
    qcalc[np.where(np.isinf(qcalc))] = -999.

    return ([qcalc, es, eb, rec])

def NSE(para, area, prec, pet, obs, i):
    #i = período de aquecimento
    dif_sim = (obs[i:] - smapm(area, para, prec, pet)[0][i:])**2
    dif_clim = (obs[i:] - obs[i:].mean())**2
    nse = -(1 - (dif_sim.sum()/dif_clim.sum()))
    return nse

#BH1 = BH7...
#%%
basins = ["BH1", "BH2", "BH3", "BH4"]

dict_period = {
    "BH1": {"P1": [1985, 1996], "P2": [1996, 2015], "area": 16795.26},
    "BH2": {"P1": [1985, 1996], "P2": [1996, 2015], "area": 30932.46},
    "BH3": {"P1": [1985, 1996], "P2": [1996, 2015], "area": 36316.00},
    "BH4": {"P1": [1985, 2000], "P2": [2000, 2015], "area": 23219.62},
}
for basin in basins:
    data = pd.read_excel("Basins_EPQ.xlsx", sheet_name = basin, index_col = 0)
    p1 = data.loc[
        (data.index.year >= dict_period[basin]["P1"][0]) &
        (data.index.year < dict_period[basin]["P1"][1])]

    p2 = data.loc[
        (data.index.year >= dict_period[basin]["P2"][0]) &
        (data.index.year <= dict_period[basin]["P2"][1])]

    initial_params = [5000, 5.84130544, 4.202310867, 6, 59.10868637, 180.130]
    bounds_params = ((400, 5000), (0.1, 10), (0, 70), (1, 6), (0, np.inf), (0, np.inf))
    area = dict_period[basin]["area"]

    # quebrar aqui
    min_win = 8 #janela mínima de anos
    warm = 12 #Mês seco + 1 ano
    p1_max = {"ini": np.nan, "fim": np.nan, "NSE": 0, "args": np.nan }
    p2_max = {"ini": np.nan, "fim": np.nan, "NSE": 0, "args": np.nan }
    with open("{} - P1.txt".format(basin), "w") as f_p1:
        f_p1.write("args = (sat, pes, crec, k, tuin, ebin) \n") 
        for i in range(0, len(p1.index), 12):
            for j in range(len(p1.index), (min_win-1)*12, -12):
                if i + j <= len(p1.index):
                    df = p1.loc[
                        (p1.index.year >= pd.date_range(p1.index[i], periods = j, freq = "M")[0].year) &
                        (p1.index.year <= pd.date_range(p1.index[i], periods = j, freq = "M")[-1].year)]
                    res = minimize (fun = NSE, x0 = initial_params, args = (area, df.P[7:], df.ETP[7:], df.Q[7:], warm), bounds = bounds_params)
                    #df.P[7:] para iniciar no último mês seco
                    f_p1.write("Periodo {} - {}; NSE = {}\n".format(
                            df.index.year[0], df.index.year[-1], -res.fun
                            ))
                    if -res.fun > p1_max["NSE"]:
                        p1_max["ini"] = df.index.year[0]
                        p1_max["fim"] = df.index.year[-1]
                        p1_max["NSE"] = -res.fun
                        p1_max["args"] = list(res.x)
                    else:
                        continue
                else:
                    continue 
        f_p1.write("##### Best NSE #####\n")
        f_p1.write("Periodo {} - {}; NSE = {}; params = {}".format(
            p1_max["ini"], p1_max["fim"], p1_max["NSE"], p1_max["args"]))
    
        with open("{} - P2.txt".format(basin), "w") as f_p2:
            f_p2.write("args = (sat, pes, crec, k, tuin, ebin) \n") 
            for i in range(0, len(p2.index), 12):
                for j in range(len(p2.index), (min_win-1)*12, -12):
                    if i + j <= len(p2.index):
                        df = p2.loc[
                            (p2.index.year >= pd.date_range(p2.index[i], periods = j, freq = "M")[0].year) &
                            (p2.index.year <= pd.date_range(p2.index[i], periods = j, freq = "M")[-1].year)]
                        res = minimize (fun = NSE, x0 = initial_params, args = (area, df.P[7:], df.ETP[7:], df.Q[7:], warm), bounds = bounds_params)
                        #df.P[7:] para iniciar no último mês seco
                        f_p2.write("Periodo {} - {}; NSE = {}\n".format(
                                df.index.year[0], df.index.year[-1], -res.fun
                                ))
                        if -res.fun > p2_max["NSE"]:
                            p2_max["ini"] = df.index.year[0]
                            p2_max["fim"] = df.index.year[-1]
                            p2_max["NSE"] = -res.fun
                            p2_max["args"] = list(res.x)
                        else:
                            continue
                    else:
                        continue 
            f_p2.write("##### Best NSE #####\n")
            f_p2.write("Periodo {} - {}; NSE = {}; params = {}".format(
                p2_max["ini"], p2_max["fim"], p2_max["NSE"], p2_max["args"]))        
# %%
