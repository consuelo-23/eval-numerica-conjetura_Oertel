import numpy as np
from itertools import combinations


def h_to_v_rep(A, b):
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
        A_sub = A[list(indice)]
        b_sub = b[list(indice)]

        punto = np.linalg.solve(A_sub, b_sub)

        # Verificar validez del punto encontrado
        if np.all(np.dot(A, punto) <= b):
            # Verificar unicidad del punto, si es único => append
            new_point = True
            for v in vertices:
                if np.allclose(v, punto):
                    new_point = False
            if new_point:
                vertices.append(punto)
        
    return np.asarray(vertices)






