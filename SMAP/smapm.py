# -*- coding: utf-8 -*-

import numpy as np

__author__ = ["Paulo Jarbas Camurca"]
__credits__ = ["Fco Vasconcelos", "Marcelo Rodrigues"]
__license__ = "GPL"
__version__ = "1.0"
__email__ = "pjarbas312@gmail.com"


def smapm(para, area, prec, pet):
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

    area=area
    m = len(para)  # 2 ou 6 parametros
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

    return qcalc
