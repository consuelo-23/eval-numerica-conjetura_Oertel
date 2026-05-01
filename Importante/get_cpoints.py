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
        
        # Chequear que A_Sub es invertiblee
        if A_sub.shape[0] != A_sub.shape[1] or np.linalg.det(A_sub) == 0:
            continue        

        # Obtener el valor de x
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
    # Trabajamos como array
    vertices_slice = np.asarray(vertices_slice)
    # Primero me quedo con las coordenadas (x,y)
    vertices = vertices_slice[:, 1:]

    # Elegir un centro
    # Podría ser el centro de Chebyshev, pero necesito su H representation para eso
    # Así que por mientra trabajo con el promedio de los puntos
    # Que es un punto interior por lo menos
    centro = np.asarray(np.mean(vertices, axis = 0))


    # Sacarle vector a los vértices desde el centro hasta cada uno
    vectores = []
    for i in vertices:
        u_i = i - centro
        vectores.append(u_i)

    # Ahora calcular el ángulo respecto al centro con cada uno de los vectores
    # El primero vector en de referencia
    u_ref = vectores[0]

    # Como arccos me entrega valores entre [0,pi], voy a ordenarlos por los puntos a su izquierda
    # y los puntos a su derecha, de menor a mayor ángulo
    # Luego los puedo juntar en una lista
    puntos_izq = {tuple(u_ref) : 0}
    puntos_der = {}
    
    vectores_a_ordenar = vectores[1:] # Sublista con los que hay que ordenar
    for i in vectores_a_ordenar:
        # Siguiendo la fórmula theta_i = arccos( <u_ref, u_i> / (||u_ref|| ||u_i||) )
        theta_i = np.arccos(np.dot(u_ref, i)/(np.linalg.norm(u_ref) * np.linalg.norm(i)))

        #determinar si quedó a la izquiera o la derecha
        det = u_ref[0]*i[1] - u_ref[1]*i[0]
        if det >= 0:
            puntos_izq.update({tuple(i) : theta_i})
        else:
            puntos_der.update({tuple(i) : theta_i})

    # Ahora hay que sortear los diccionarios según ángulo
    puntos_ordenados_izq = dict(sorted(puntos_izq.items(), key = lambda item : item[1]))
    puntos_ordenados_der = dict(sorted(puntos_der.items(), key = lambda item : item[1]))

    # Y juntar las listas
    puntos_ordenados = []

    for i in puntos_ordenados_izq.keys():
        puntos_ordenados.append(i)
    for i in reversed(puntos_ordenados_der.keys()):
        puntos_ordenados.append(i)
       
        
    return puntos_ordenados