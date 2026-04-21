import numpy as np
from vol_star import  _choose_batch
from scipy.spatial import ConvexHull

#primero, averiguar cómo pasar de H representation a V representation


def h_to_v_rep(A, b, tol = 1e-9):
    """
    Obtiene la V-representation de un cuerpo convexo a partir de la H-representation
    A : Matriz de coeficientes (m x n)
    b : Vector (m)
    """
    m, n = A.shape # n debería ser 3
    vertices = []

    # Buscamos intersecciones de 3 planos
    for indice in combinations(range(m),n):
        # Seleccionamos las 3 filas correspondientes a los planos


    return vertices







