import numpy as np
from itertools import combinations
from Hit_and_Run import CentroChebyshev


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
        # Seleccionamos las 3 filas correspondientes a los planos mediante combinación de los índices
        A_sub = A[list(indice)]
        b_sub = b[list(indice)]
        
        # Falta chequear que A_Sub es invertible
        
        punto = np.linalg.solve(A_sub, b_sub)

        # Verificar validez del punto encontrado
        if np.all(np.dot(A, punto) <= b):
            # Verificar unicidad del punto
            new_point = True
            for v in vertices:
                if np.allclose(v, punto): # Si los puntos son iguales tira True, sino False
                    new_point = False
                    break
            if new_point: # Si es único => append
                vertices.append(punto)
        
    return np.asarray(vertices)


def ordenar_vertices(A, b):
    """
    ordenar los vértices para poder ocupar la fórmula en la sgte función
    """
    center, radio = CentroChebyshev(A,b)

    vertices = h_to_v_rep(A,b)
    
    return



def get_centerpoints(A, b):
    """
    obtener los candidatos a centerpoints estratégicos utilizando la fórmula de showlace
    """
    return



