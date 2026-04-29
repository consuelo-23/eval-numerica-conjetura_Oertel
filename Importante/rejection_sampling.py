import numpy as np
from scipy.optimize import linprog
import time as time

#encontrar puntos interiores
def obtener_caja(A,b):
    n_dims = A.shape[1]
    limits = []

    for i in range(n_dims):
        #función objetivo: minimizar x_i
        c = np.zeros(n_dims)
        c[i] = 1

        #encontrar minimo y máximo de la dimensión i
        sol_min = linprog(c, A_ub=A, b_ub=b, bounds=[(None, None)])
        sol_max = linprog(-c, A_ub=A, b_ub=b, bounds=[(None, None)])

        if sol_min.success and sol_max.success:
            limits.append((sol_min.fun, -sol_max.fun))
        else:
            limits.append((0,0))

    return limits

def EstimateVolumeRejection(A, b, samples=10**7):
    #start_time = time.time()
    #inicialización
    n = A.shape[1]
    limites = obtener_caja(A,b)

    mins = np.array([lim[0] for lim in limites])
    maxs = np.array([lim[1] for lim in limites])
    volumen_caja = np.prod(maxs - mins)

    #muestre0

    puntos = np.random.uniform(mins, maxs, size=(samples, n))

    dentro = np.all(np.dot(puntos, A.T) <= b, axis=1)

    volumen = np.sum(dentro) / samples * volumen_caja

    return volumen #time.time() - start_time