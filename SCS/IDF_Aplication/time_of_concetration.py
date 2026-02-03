import numpy as np

def Kirpich(L, hf, hi):
    
    tc = 57*np.power((np.power(L,3)/(hi-hf)), 0.385)
    
    return tc

def Kirpich_modificado(L, hf, hi):
    
    tc = 85.2*np.power((np.power(L,3)/(hi-hf)), 0.385)

    return tc

def USACE(L, hf, hi):

    S = (hi - hf) / (L * 1000)
    tc = 0.191 * np.power(L, 0.76) * np.power(S, -0.19)
    tc = tc * 60
    return tc