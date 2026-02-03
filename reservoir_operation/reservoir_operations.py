'''
Autor: Carlos Eduardo Sousa Lima, M. Sc
e-mail: carlosesl07@gmail.com
Departamento de Engenharia Hidráulica e Ambiental/ Universidade Federal do Ceará (DEHA/UFC)
Doutorando em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Mestre em Engenharia Civil (Recursos Hídricos) - DEHA/UFC
Engenheiro Civil com ênfase em Meio Ambiente - Universidade Estadual Vale do Acaraú (UVA)
'''
#%%
import numpy as np
from scipy.optimize import minimize
import pickle as pkl
import os

def get_cap (cota, volume, cs):

    if (cota == cs).any():

        cap = volume[np.where(cota == cs)]
    
    else:

        cap = np.interp(cs, cota, volume)

    return cap[0]


def optimize_alpha_beta(params, area, volume):
    a, b = params

    area_calc = a*np.power(volume,b)

    return np.sum(np.power(area - area_calc,2))

def get_alpha_beta(area, volume):

    path_params = "params_reserv.pkl"

    if os.path.exists(path_params):
        with open(path_params, "rb") as file:
            params = pkl.load(file)

    else:
        
        params = minimize(optimize_alpha_beta,
            x0 = [0.5,0.5], 
            args = (area, volume)).x

        with open("params_reserv.pkl", "wb") as file:
            pkl.dump(params, file)
    
    return params

def evaporation_loss(storage, alpha, beta, mon_evap):

    if storage < 0.001:
        er = 0
    else:
        er = (alpha*np.power(storage, beta)) * mon_evap
    
    return er

def regularization_loss(storage, er, reg):

    if (storage - er) > reg:
        reg = reg
    else:
        reg = np.max([0, storage - er])

    return reg

def mon_operation(Q_reg, max_storage, S0, inflow, evap, alpha, beta): 

    #Si, Qin, Evap, Er1, Re1, V2, Evap2, Re2, Sf, Vert
    operation_matrix = np.full(shape = (len(inflow), 10), fill_value = np.nan)

    #Initializing values
    
    operation_matrix[:,1] = (inflow["Q"]/np.power(10,6)) * 30.4 * 86400
    operation_matrix[:,2] = np.divide(evap, 1000)

    for i in range(operation_matrix.shape[0]):
        if i == 0:
            operation_matrix[i,0] = S0
        else:
            operation_matrix[i,0] = operation_matrix[i-1,8] - operation_matrix[i-1,9]

        S = np.sum(operation_matrix[i,0:2]) #np.sum(operation_matrix[i, 0:2]) = S0 + inflow
        
        operation_matrix[i,3] = evaporation_loss(storage = S, 
                                    alpha = alpha, beta = beta, mon_evap = operation_matrix[i,2]/2)
        
        operation_matrix[i,4] = regularization_loss(storage = S, 
                                    er = operation_matrix[i,3], reg = Q_reg/2)

        if S - np.sum(operation_matrix[i,3:5]) < 0: #Ensure that values, such as -1 × 10^-16, are not equal to zero.

            operation_matrix[i,5] = 0

        else:

            operation_matrix[i,5] = S - np.sum(operation_matrix[i,3:5])
 

        operation_matrix[i,6] = evaporation_loss(storage = operation_matrix[i,5], 
                                    alpha = alpha, beta = beta, mon_evap = operation_matrix[i,2]/2)
        
        operation_matrix[i,7] = regularization_loss(storage = operation_matrix[i,5],
                                    er = operation_matrix[i,6], reg = Q_reg/2)
        
        operation_matrix[i,8] = operation_matrix[i,5] - np.sum(operation_matrix[i,6:8])

        operation_matrix[i,9] = np.max([operation_matrix[i,8] - max_storage, 0])
        
    return operation_matrix

def optimize_operation(param, max_storage, S0, inflow, evap, alpha, beta, permanence):

    Q_reg = param

    operation = mon_operation(Q_reg, max_storage, S0, inflow, evap, alpha, beta)

    reg_sum = operation[:,4] + operation[:,7]

    mask = reg_sum < Q_reg
    fail_rate = np.mean(mask)

    #fail_rate varies in steps
    #use the minimize_scalar function, 
    #minimize will not be able to calculate the gradient (there is no continuous variation)

    cost = abs(fail_rate - (1-permanence))

    return cost

def main():
    
    return
if __name__ == "__main__":
    main()
