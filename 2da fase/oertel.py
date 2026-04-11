# oertel.py
import numpy as np
from numpy.linalg import norm  # por si lo usas en otros lugares
from typing import List, Tuple, Optional

from rejection_sampling import EstimateVolumeRejection  # si ya no lo usas, lo puedes borrar
from vol_star import ratio_cp


def _inside(A: np.ndarray, b: np.ndarray, x: np.ndarray, tol: float = 1e-9) -> bool:
    """Chequea si x cumple Ax <= b (con tolerancia)."""
    return bool(np.all(A @ x <= b + tol))

def oertel(A, b, d,
           puntos_test, #lista [v0, v1, v2, va]
           z_vals = [0,1,2],
           N_hip = 2000,
           N = 10**6,
           tol = 1e-9,
           batch = None,
           target_mb = None):
    
    """
    Busca un centerpoint aproximado maximizando:
        F(cp) = min_u  [ sum_z min(Vol(S_z ∩ H_u^+), Vol(S_z ∩ H_u^-)) ] / sum_z Vol(S_z)

    Devuelve:
    bestCP : mejor centerpoint
    bestF : valor de F(bestCP)
    bestU : dirección que produce el peor corte para bestCP
    """
    #--------- búsqueda de centerpoint sobre puntos específicos ------
    bestF = -np.inf
    bestCP = None
    bestU = None
    

    for candidato in puntos_test: #iterar sobre los centerpoints candidatos
        cp = np.asarray(candidato, dtype = float) #verificar que sea array

        if not _inside(A, b, cp, tol=tol):
            print(f"Punto {cp} fuera de los límites, me lo salto")
            continue

        #evaluar el ratio de oertel

        F_cp, u_cp = ratio_cp(
            A, b, cp, z_vals, N_hip, d, N, tol=tol, batch= batch, target_mb=target_mb)
        #que tan central es el punto

        print(f"Punto{cp} -> F: {F_cp}")

        #guardamos el mejor de los 4 puntos
        if F_cp > bestF:
            bestF = float(F_cp)
            bestCP = cp.copy()
            bestU = np.asarray(u_cp, dtype = float)
        
    return bestCP, float(bestF), bestU


def linea_de_ensayo(v1, va, N_Muestras = 50):
    v1 = np.asarray(v1)
    va = np.asarray(va)

    
    t = np.linspace(0,1,N_Muestras) 
    #retorna números equitativamente espaciados entre 0 y 1

    muestras = []
    for i in t:
        muestra = (1-i)*v1 + i*va
        muestras.append(muestra)
    return muestras
    



def ortel(
    A: np.ndarray,
    b: np.ndarray,
    d: int,
    z_vals: Optional[List[int]] = None,
    N_cp: int = 100,        # nº de CPs candidatos
    N_hip: int = 2000,     # nº de hiperplanos aleatorios (direcciones)
    N: int = 10**5,       # nº de muestras MC para volúmenes relativos
    tol: float = 1e-9,
    batch: Optional[int] = None,
    target_mb=None,
) -> Tuple[np.ndarray, float, np.ndarray]:
    """
    Busca un centerpoint aproximado maximizando:
        F(cp) = min_u  [ sum_z min(Vol(S_z ∩ H_u^+), Vol(S_z ∩ H_u^-)) ] / sum_z Vol(S_z)

    Retorna
    -------
    bestCP : np.ndarray (1+d,), el mejor cp encontrado
    bestF  : float, valor de F(bestCP)
    bestU  : np.ndarray (d,), dirección que produce el peor corte para bestCP
    """
    # -------- fibras (z) --------
    if z_vals is None:
        z_vals = [0, 1, 2]
    z_vals = [int(z) for z in z_vals]
    z_vals_arr = np.array(z_vals, dtype=int)

    # -------- chequeos básicos --------
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    if A.ndim != 2 or b.ndim != 1 or A.shape[0] != b.shape[0] or A.shape[1] != 1 + d:
        raise ValueError(
            f"Dimensiones incompatibles: A {A.shape}, b {b.shape}, d={d} (esperado A.shape[1] = 1+d)."
        )

    # -------- búsqueda de CP --------
    bestF: float = -np.inf
    bestCP: Optional[np.ndarray] = None
    bestU: Optional[np.ndarray] = None

    for _ in range(int(N_cp)):
        # Muestreamos un cp candidato en z × [0,1]^d:
        z_cp = int(np.random.choice(z_vals_arr))
        p_cp = np.random.rand(d)                 # (d,)   
        cp = np.concatenate([[float(z_cp)], p_cp]).astype(float)

        # Debe caer dentro de la envolvente
        if not _inside(A, b, cp, tol=tol):
            continue #se salta a la sgte iteración del for

        # Evalúa F(cp) con N_hip direcciones y N muestras por fibra
        F_cp, u_cp = ratio_cp(
            A, b, cp, z_vals, N_hip, d, N,
            tol=tol, batch=batch, target_mb=target_mb
        )

        if F_cp > bestF:
            bestF = float(F_cp)
            bestCP = cp.copy()
            bestU = np.asarray(u_cp, dtype=float)
    

    # Fallback: intenta encontrar un cp válido si no hubo suerte
    if bestCP is None:
        for _ in range(1000):
            z_cp = int(np.random.choice(z_vals_arr))
            p_cp = np.random.rand(d)
            cp_try = np.concatenate([[float(z_cp)], p_cp])
            if _inside(A, b, cp_try, tol=tol):
                F_cp, u_cp = ratio_cp(
                    A, b, cp_try, z_vals, N_hip, d, N,
                    tol=tol, batch=batch, target_mb=target_mb
                )
                bestCP = cp_try.astype(float)
                bestF = float(F_cp)
                bestU = np.asarray(u_cp, dtype=float)
                break

    if bestCP is None:
        # Último recurso: algo consistente
        bestCP = np.zeros(1 + d, dtype=float)
        bestF = float(0.0)
        bestU = np.zeros(d, dtype=float)

    if bestU is None:
        bestU = np.zeros(d, dtype=float)

    return bestCP, float(bestF), bestU