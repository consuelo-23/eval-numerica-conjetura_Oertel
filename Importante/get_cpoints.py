import numpy as np
from itertools import combinations
from Hit_and_Run import CentroChebyshev
import bisect



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

# Tengo que sacar los vertices por cada slice
# Luego los ordeno

def ordenar_vertices(vertices_slice):
    """
    ordenar los vértices (de cada slice) para poder ocupar la fórmula en la sgte función
    input:
        vertices_slice : vértices por correspondientes a cada slice
    """
    # Provisoriamente voy a sacarles la envoltura convexa, a ver qué pasa
    hull = ConvexHull(vertices_slice, qhull_options = "QJ")
    A = hull.equations[:, :-1]
    b = -hull.equations[:, -1]
    
    center, radio = CentroChebyshev(A,b)


    # Sacarle vector a los vértices desde el centro hasta cada uno
    vectores = []
    for i in vertices_slice:
        u_i = vertices_slice[i] - CentroChebyshev
        vectores.append(u_i)

    # Ahora calcular el ángulo respecto al centro con cada uno de los vectores
    u_ref = vectores[0]
    puntos_ordenados_izq = {}
    puntos_ordenados_der = {}
    vectores_a_ordenar = vectores[1:] # Sublista con los que hay que ordenar
    for i in vectores_a_ordenar:
        # Siguiendo la fórmula theta_i = arccos( <u_ref, u_i> / (||u_ref|| ||u_i||) )
        theta_i = np.arccos(np.dot(u_ref, i)/(np.linalg.norm(u_ref) * np.linalg.norm(i)))

        #determinar si quedó a la izquiera o la derecha
        det = u_ref[0]*i[1] - u_ref[1]*i[0]
        if det >= 0:
            puntos_ordenados_izq.update({i : theta_i})
        else:
            puntos_ordenados_der.update({i : theta_i})
        
        
    return



def get_centerpoints(A, b):
    """
    obtener los candidatos a centerpoints estratégicos utilizando la fórmula de showlace
    """
    return



